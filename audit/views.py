from datetime import datetime

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.decorators import role_required
from cashbox.models import Payment
from vehicles.models import VehicleEntry

from .models import Reconciliation
from .services import run_reconciliation


@role_required('admin')
def reconciliation_view(request):
    date_param = request.GET.get('data')
    if date_param:
        target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
    else:
        target_date = timezone.localdate()

    cases = list(run_reconciliation(target_date))
    order = {
        Reconciliation.Status.NO_ENTRY: 0,
        Reconciliation.Status.NO_PAYMENT: 1,
        Reconciliation.Status.VALUE_MISMATCH: 2,
        Reconciliation.Status.SERVICE_MISMATCH: 3,
        Reconciliation.Status.UNVERIFIABLE: 4,
        Reconciliation.Status.OK: 5,
    }
    cases.sort(key=lambda c: order.get(c.status, 9))

    unverifiable_entries = [c for c in cases if c.status == Reconciliation.Status.UNVERIFIABLE and c.vehicle_entry_id]
    unverifiable_payments = [c for c in cases if c.status == Reconciliation.Status.UNVERIFIABLE and c.payment_id]
    linkable_cases = [c for c in cases if c.status != Reconciliation.Status.UNVERIFIABLE]

    summary = {
        'entries_count': VehicleEntry.objects.filter(is_trashed=False, created_at__date=target_date).count(),
        'payments_count': Payment.objects.filter(created_at__date=target_date).count(),
        'ok_count': sum(1 for c in cases if c.status == Reconciliation.Status.OK),
        'divergence_count': sum(
            1 for c in cases
            if c.status in (
                Reconciliation.Status.SERVICE_MISMATCH,
                Reconciliation.Status.VALUE_MISMATCH,
                Reconciliation.Status.NO_PAYMENT,
                Reconciliation.Status.NO_ENTRY,
            )
        ),
        'no_payment_count': sum(1 for c in cases if c.status == Reconciliation.Status.NO_PAYMENT),
        'no_entry_count': sum(1 for c in cases if c.status == Reconciliation.Status.NO_ENTRY),
    }

    return render(request, 'audit/reconciliation.html', {
        'target_date': target_date,
        'cases': linkable_cases,
        'unverifiable_entries': unverifiable_entries,
        'unverifiable_payments': unverifiable_payments,
        'summary': summary,
        'investigation_choices': Reconciliation.Investigation.choices,
    })


@role_required('admin')
def update_investigation(request, pk):
    case = get_object_or_404(Reconciliation, pk=pk)
    if request.method != 'POST':
        return redirect('audit:reconciliation')

    investigation_status = request.POST.get('investigation_status')
    review_note = request.POST.get('review_note', '')
    valid_statuses = dict(Reconciliation.Investigation.choices)
    if investigation_status in valid_statuses:
        case.investigation_status = investigation_status
        case.review_note = review_note
        case.reviewed_by = request.user
        case.reviewed_at = timezone.now()
        case.save()
        messages.success(request, 'Caso atualizado.')
    else:
        messages.error(request, 'Estado de investigação inválido.')

    redirect_date = request.POST.get('data', '')
    url = reverse('audit:reconciliation')
    if redirect_date:
        url = f'{url}?data={redirect_date}'
    return redirect(url)


@role_required('admin')
def manual_link(request):
    if request.method != 'POST':
        return redirect('audit:reconciliation')

    entry_pk = request.POST.get('vehicle_entry_id')
    payment_pk = request.POST.get('payment_id')
    target_date = request.POST.get('data') or timezone.localdate().isoformat()

    entry = get_object_or_404(VehicleEntry, pk=entry_pk) if entry_pk else None
    payment = get_object_or_404(Payment, pk=payment_pk) if payment_pk else None

    if not entry and not payment:
        messages.error(request, 'Selecione pelo menos um registo para ligar.')
        return redirect(f"{reverse('audit:reconciliation')}?data={target_date}")

    expected_value = entry.service.price if entry and entry.service_id else None
    received_value = payment.amount if payment else None
    status = Reconciliation.Status.UNVERIFIABLE
    value_difference = None
    if entry and payment:
        if expected_value is not None and received_value is not None and expected_value != received_value:
            status = Reconciliation.Status.VALUE_MISMATCH
            value_difference = expected_value - received_value
        else:
            status = Reconciliation.Status.OK
    elif entry:
        status = Reconciliation.Status.NO_PAYMENT
    elif payment:
        status = Reconciliation.Status.NO_ENTRY

    Reconciliation.objects.create(
        date=datetime.strptime(target_date, '%Y-%m-%d').date(),
        vehicle_entry=entry,
        payment=payment,
        status=status,
        expected_value=expected_value,
        received_value=received_value,
        value_difference=value_difference,
        investigation_status=Reconciliation.Investigation.RESOLVIDO,
        reviewed_by=request.user,
        reviewed_at=timezone.now(),
        review_note='Ligação manual feita pelo admin (registo sem matrícula).',
    )
    messages.success(request, 'Registos ligados manualmente.')
    return redirect(f"{reverse('audit:reconciliation')}?data={target_date}")
