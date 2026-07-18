from django.contrib import messages
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_required

from .forms import VehicleEntryEditForm, VehicleEntryForm, VehicleEntryTrashForm
from .models import VehicleEntry, VehicleEntryLog


def _list_context(**overrides):
    entries = VehicleEntry.objects.filter(is_trashed=False)
    rows = [
        (entry, VehicleEntryEditForm(instance=entry), VehicleEntryTrashForm())
        for entry in entries
    ]
    context = {
        'entries': entries,
        'rows': rows,
        'pending_count': entries.filter(status=VehicleEntry.Status.PENDENTE).count(),
        'create_form': VehicleEntryForm(),
        'open_create': False,
        'open_edit_pk': None,
        'open_trash_pk': None,
    }
    context.update(overrides)
    return context


@role_required('seguranca')
def vehicle_home(request):
    today_entries = VehicleEntry.objects.filter(is_trashed=False, created_at__date=timezone.localdate())
    return render(request, 'vehicles/home.html', {
        'today_entries': today_entries,
        'today_count': today_entries.count(),
    })


@role_required('seguranca')
def vehicle_list(request):
    open_create = request.GET.get('open') == 'create'
    return render(request, 'vehicles/list.html', _list_context(open_create=open_create))


@role_required('seguranca')
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.registered_by = request.user
            entry.save()
            messages.success(request, 'Carro registado com sucesso.')
            return redirect('vehicles:list')
        return render(request, 'vehicles/list.html', _list_context(create_form=form, open_create=True))
    return redirect('vehicles:list')


@role_required('seguranca')
def vehicle_edit(request, pk):
    entry = get_object_or_404(VehicleEntry, pk=pk, is_trashed=False)
    if request.method != 'POST':
        return redirect('vehicles:list')

    before = model_to_dict(entry, fields=['brand', 'model', 'plate', 'service'])
    form = VehicleEntryEditForm(request.POST, request.FILES, instance=entry)
    if form.is_valid():
        reason = form.cleaned_data['reason']
        entry = form.save()
        after = model_to_dict(entry, fields=['brand', 'model', 'plate', 'service'])
        VehicleEntryLog.objects.create(
            entry=entry, changed_by=request.user, reason=reason,
            snapshot={'before': str(before), 'after': str(after)},
        )
        messages.success(request, 'Registo atualizado.')
        return redirect('vehicles:list')

    context = _list_context(open_edit_pk=entry.pk)
    context['rows'] = [
        (e, form, trash_form) if e.pk == entry.pk else (e, edit_form, trash_form)
        for e, edit_form, trash_form in context['rows']
    ]
    return render(request, 'vehicles/list.html', context)


@role_required('seguranca')
def vehicle_trash(request, pk):
    entry = get_object_or_404(VehicleEntry, pk=pk, is_trashed=False)
    if request.method != 'POST':
        return redirect('vehicles:list')

    form = VehicleEntryTrashForm(request.POST)
    if form.is_valid():
        entry.is_trashed = True
        entry.trash_reason = form.cleaned_data['reason']
        entry.trashed_by = request.user
        entry.trashed_at = timezone.now()
        entry.save()
        messages.success(request, 'Registo movido para o lixo.')
        return redirect('vehicles:list')

    context = _list_context(open_trash_pk=entry.pk)
    context['rows'] = [
        (e, edit_form, form) if e.pk == entry.pk else (e, edit_form, trash_form)
        for e, edit_form, trash_form in context['rows']
    ]
    return render(request, 'vehicles/list.html', context)


@role_required('seguranca')
def vehicle_adopt(request, pk):
    entry = get_object_or_404(VehicleEntry, pk=pk, is_trashed=False, status=VehicleEntry.Status.PENDENTE)
    entry.status = VehicleEntry.Status.ADOTADO
    entry.claimed_by = request.user
    entry.claimed_at = timezone.now()
    entry.save()
    messages.success(request, 'Registo adotado.')
    return redirect('vehicles:list')


@role_required('admin')
def vehicle_trash_list(request):
    entries = VehicleEntry.objects.filter(is_trashed=True).prefetch_related('logs')
    return render(request, 'vehicles/trash_list.html', {'entries': entries})
