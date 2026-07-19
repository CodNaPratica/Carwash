import json
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from vehicles.models import VehicleType

from .forms import ServiceForm, ServiceQuickForm
from .models import Service, ServicePrice


def _price_rows(service, vehicle_types, existing_by_service):
    existing = existing_by_service.get(service.pk, {})
    return [(vt, existing.get(vt.pk)) for vt in vehicle_types]


def _list_context(**overrides):
    services = Service.objects.all()
    vehicle_types = VehicleType.objects.all()
    existing_by_service = {}
    for sp in ServicePrice.objects.select_related('service', 'vehicle_type'):
        existing_by_service.setdefault(sp.service_id, {})[sp.vehicle_type_id] = sp.price
    rows = [
        (service, ServiceForm(instance=service), _price_rows(service, vehicle_types, existing_by_service))
        for service in services
    ]
    context = {
        'services': services,
        'rows': rows,
        'vehicle_types': vehicle_types,
        'create_form': ServiceForm(initial={'active': True}),
        'open_create': False,
        'open_edit_pk': None,
    }
    context.update(overrides)
    return context


@role_required('admin')
def service_list(request):
    return render(request, 'services/list.html', _list_context())


@role_required('admin')
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Serviço criado com sucesso.')
            return redirect('services:list')
        return render(request, 'services/list.html', _list_context(create_form=form, open_create=True))
    return redirect('services:list')


@role_required('admin')
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method != 'POST':
        return redirect('services:list')

    form = ServiceForm(request.POST, instance=service)
    if form.is_valid():
        form.save()
        messages.success(request, 'Serviço atualizado.')
        return redirect('services:list')

    context = _list_context(open_edit_pk=service.pk)
    context['rows'] = [
        (s, form, price_rows) if s.pk == service.pk else (s, edit_form, price_rows)
        for s, edit_form, price_rows in context['rows']
    ]
    return render(request, 'services/list.html', context)


@role_required('admin')
def service_prices_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method != 'POST':
        return redirect('services:list')

    for vt in VehicleType.objects.all():
        raw = (request.POST.get(f'price_{vt.pk}') or '').strip()
        if not raw:
            ServicePrice.objects.filter(service=service, vehicle_type=vt).delete()
            continue
        try:
            value = Decimal(raw)
        except InvalidOperation:
            continue
        ServicePrice.objects.update_or_create(service=service, vehicle_type=vt, defaults={'price': value})

    messages.success(request, f'Preços de "{service.name}" atualizados.')
    return redirect('services:list')


@role_required('tesoureira')
@require_POST
def service_quick_create(request):
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        payload = request.POST

    form = ServiceQuickForm(payload)
    if form.is_valid():
        service = form.save()
        return JsonResponse({'id': service.id, 'name': service.name, 'price': str(service.price)})
    return JsonResponse({'errors': form.errors}, status=400)


@role_required('tesoureira')
def service_price_lookup(request):
    service_id = request.GET.get('service')
    vehicle_type_id = request.GET.get('vehicle_type')
    service = Service.objects.filter(pk=service_id).first()
    if not service:
        return JsonResponse({'error': 'Serviço não encontrado.'}, status=404)
    vehicle_type = VehicleType.objects.filter(pk=vehicle_type_id).first()
    return JsonResponse({'price': str(service.price_for(vehicle_type))})
