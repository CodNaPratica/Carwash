from django.contrib import messages
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.decorators import role_required

from .forms import VehicleEntryEditForm, VehicleEntryForm, VehicleEntryTrashForm, VehicleTypeForm
from .models import VehicleEntry, VehicleEntryLog, VehicleType


def _list_context(user, **overrides):
    entries = VehicleEntry.objects.filter(is_trashed=False).prefetch_related('logs')
    rows = [
        (entry, VehicleEntryEditForm(instance=entry, user=user), VehicleEntryTrashForm())
        for entry in entries
    ]
    vehicle_types = VehicleType.objects.select_related('added_by').all()
    context = {
        'entries': entries,
        'rows': rows,
        'pending_count': entries.filter(status=VehicleEntry.Status.PENDENTE).count(),
        'create_form': VehicleEntryForm(user=user),
        'open_create': False,
        'open_edit_pk': None,
        'open_trash_pk': None,
        'vehicle_types': vehicle_types,
        'type_pending_count': vehicle_types.filter(is_approved=False).count(),
        'type_create_form': VehicleTypeForm(initial={'is_approved': True}),
        'open_types_modal': False,
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
    open_param = request.GET.get('open')
    return render(request, 'vehicles/list.html', _list_context(
        request.user, open_create=open_param == 'create', open_types_modal=open_param == 'types',
    ))


@role_required('seguranca')
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleEntryForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.registered_by = request.user
            entry.save()
            messages.success(request, 'Carro registado com sucesso.')
            return redirect('vehicles:list')
        return render(request, 'vehicles/list.html', _list_context(request.user, create_form=form, open_create=True))
    return redirect('vehicles:list')


@role_required('seguranca')
def vehicle_edit(request, pk):
    entry = get_object_or_404(VehicleEntry, pk=pk, is_trashed=False)
    if request.method != 'POST':
        return redirect('vehicles:list')

    before = model_to_dict(entry, fields=['brand', 'model', 'plate', 'service'])
    form = VehicleEntryEditForm(request.POST, request.FILES, instance=entry, user=request.user)
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

    context = _list_context(request.user, open_edit_pk=entry.pk)
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

    context = _list_context(request.user, open_trash_pk=entry.pk)
    context['rows'] = [
        (e, edit_form, form) if e.pk == entry.pk else (e, edit_form, trash_form)
        for e, edit_form, trash_form in context['rows']
    ]
    return render(request, 'vehicles/list.html', context)


@role_required('seguranca')
def vehicle_complete(request, pk):
    entry = get_object_or_404(VehicleEntry, pk=pk, is_trashed=False, status=VehicleEntry.Status.PENDENTE)
    entry.status = VehicleEntry.Status.CONCLUIDO
    entry.completed_by = request.user
    entry.completed_at = timezone.now()
    entry.save()
    messages.success(request, 'Registo marcado como concluído.')
    return redirect('vehicles:list')


@role_required('admin')
def vehicle_trash_list(request):
    entries = VehicleEntry.objects.filter(is_trashed=True).prefetch_related('logs')
    return render(request, 'vehicles/trash_list.html', {'entries': entries})


@role_required('admin')
def vehicle_restore(request, pk):
    entry = get_object_or_404(VehicleEntry, pk=pk, is_trashed=True)
    if request.method != 'POST':
        return redirect('vehicles:trash_list')
    VehicleEntryLog.objects.create(
        entry=entry, changed_by=request.user,
        reason=f'Restaurado do lixo pelo admin (motivo original da eliminação: {entry.trash_reason})',
        snapshot={'action': 'restore'},
    )
    entry.is_trashed = False
    entry.trash_reason = ''
    entry.trashed_by = None
    entry.trashed_at = None
    entry.save()
    messages.success(request, 'Registo restaurado com sucesso.')
    return redirect('vehicles:trash_list')


@role_required('admin')
def vehicle_permanent_delete(request, pk):
    entry = get_object_or_404(VehicleEntry, pk=pk, is_trashed=True)
    if request.method != 'POST':
        return redirect('vehicles:trash_list')
    entry.delete()
    messages.success(request, 'Registo eliminado definitivamente.')
    return redirect('vehicles:trash_list')


@role_required('admin')
def vehicle_type_create(request):
    if request.method == 'POST':
        form = VehicleTypeForm(request.POST)
        if form.is_valid():
            vehicle_type = form.save(commit=False)
            vehicle_type.is_approved = True
            vehicle_type.save()
            messages.success(request, 'Tipo de veículo criado.')
            return redirect(f"{reverse('vehicles:list')}?open=types")
        return render(request, 'vehicles/list.html', _list_context(
            request.user, type_create_form=form, open_types_modal=True,
        ))
    return redirect('vehicles:list')


@role_required('admin')
def vehicle_type_approve(request, pk):
    vehicle_type = get_object_or_404(VehicleType, pk=pk)
    if request.method != 'POST':
        return redirect('vehicles:list')
    vehicle_type.is_approved = True
    vehicle_type.save()
    messages.success(request, f'Tipo "{vehicle_type.name}" aprovado.')
    return redirect(f"{reverse('vehicles:list')}?open=types")


@role_required('admin')
def vehicle_type_delete(request, pk):
    vehicle_type = get_object_or_404(VehicleType, pk=pk)
    if request.method != 'POST':
        return redirect('vehicles:list')
    name = vehicle_type.name
    vehicle_type.delete()
    messages.success(request, f'Tipo "{name}" apagado. Registos que o usavam ficam sem tipo definido.')
    return redirect(f"{reverse('vehicles:list')}?open=types")
