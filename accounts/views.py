from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from cashbox.models import CashClosure
from cashbox.services import totals_for_range
from vehicles.models import VehicleEntry

from .decorators import role_required
from .forms import CwPasswordChangeForm, ProfileForm, SetPasswordForm, UserCreateForm, UserEditForm
from .models import User


@login_required
def dashboard(request):
    user = request.user
    if user.is_admin_role():
        return redirect('admin_dashboard')
    if user.is_seguranca():
        return redirect('vehicles:home')
    if user.is_tesoureira():
        return redirect('cashbox:home')
    return redirect('login')


@role_required('admin')
def admin_dashboard(request):
    today = timezone.localdate()
    pending_count = VehicleEntry.objects.filter(is_trashed=False, status=VehicleEntry.Status.PENDENTE).count()
    trashed_count = VehicleEntry.objects.filter(is_trashed=True).count()
    users_count = User.objects.count()
    total_in, total_out = totals_for_range(today, today)

    total_moved = total_in + total_out
    in_pct = round((total_in / total_moved) * 100) if total_moved else 0
    out_pct = 100 - in_pct if total_moved else 0

    last_closure = CashClosure.objects.order_by('-date_end').first()

    return render(request, 'accounts/admin_dashboard.html', {
        'pending_count': pending_count,
        'trashed_count': trashed_count,
        'users_count': users_count,
        'total_in': total_in,
        'total_out': total_out,
        'balance': total_in - total_out,
        'in_pct': in_pct,
        'out_pct': out_pct,
        'last_closure': last_closure,
    })


def _user_list_context(**overrides):
    users = User.objects.all().order_by('username')
    rows = [(u, UserEditForm(instance=u), SetPasswordForm()) for u in users]
    context = {
        'users': users,
        'rows': rows,
        'create_form': UserCreateForm(),
        'open_create': False,
        'open_edit_pk': None,
        'open_password_pk': None,
    }
    context.update(overrides)
    return context


@role_required('admin')
def user_list(request):
    return render(request, 'accounts/user_list.html', _user_list_context())


@role_required('admin')
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilizador criado com sucesso.')
            return redirect('user_list')
        return render(request, 'accounts/user_list.html', _user_list_context(create_form=form, open_create=True))
    return redirect('user_list')


@role_required('admin')
def user_edit(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method != 'POST':
        return redirect('user_list')

    form = UserEditForm(request.POST, instance=user_obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Utilizador atualizado.')
        return redirect('user_list')

    context = _user_list_context(open_edit_pk=user_obj.pk)
    context['rows'] = [
        (u, form, pw_form) if u.pk == user_obj.pk else (u, edit_form, pw_form)
        for u, edit_form, pw_form in context['rows']
    ]
    return render(request, 'accounts/user_list.html', context)


@role_required('admin')
def user_set_password(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method != 'POST':
        return redirect('user_list')

    form = SetPasswordForm(request.POST)
    if form.is_valid():
        user_obj.set_password(form.cleaned_data['new_password'])
        user_obj.save()
        messages.success(request, f'Palavra-passe de {user_obj.username} atualizada.')
        return redirect('user_list')

    context = _user_list_context(open_password_pk=user_obj.pk)
    context['rows'] = [
        (u, edit_form, form) if u.pk == user_obj.pk else (u, edit_form, pw_form)
        for u, edit_form, pw_form in context['rows']
    ]
    return render(request, 'accounts/user_list.html', context)


@login_required
def profile(request):
    profile_form = ProfileForm(instance=request.user)
    password_form = CwPasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if request.POST.get('form_type') == 'profile':
            profile_form = ProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Dados atualizados.')
                return redirect('profile')
        elif request.POST.get('form_type') == 'password':
            password_form = CwPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user_obj = password_form.save()
                update_session_auth_hash(request, user_obj)
                messages.success(request, 'Palavra-passe alterada com sucesso.')
                return redirect('profile')

    return render(request, 'accounts/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })
