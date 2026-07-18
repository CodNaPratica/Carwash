import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required

from .forms import ServiceForm, ServiceQuickForm
from .models import Service


def _list_context(**overrides):
    services = Service.objects.all()
    rows = [(service, ServiceForm(instance=service)) for service in services]
    context = {
        'services': services,
        'rows': rows,
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
        (s, form) if s.pk == service.pk else (s, edit_form)
        for s, edit_form in context['rows']
    ]
    return render(request, 'services/list.html', context)


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
