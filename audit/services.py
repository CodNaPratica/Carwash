from datetime import timedelta

from cashbox.models import Payment
from vehicles.models import VehicleEntry

from .models import Reconciliation

MAX_MATCH_WINDOW = timedelta(hours=4)


def _normalize_plate(plate):
    return (plate or '').strip().upper()


def run_reconciliation(target_date):
    """Cruza os registos do segurança (VehicleEntry) com os da tesoureira (Payment)
    do dia indicado, por matrícula + serviço + horário mais próximo, e guarda o
    resultado em Reconciliation - preservando os casos já investigados pelo admin."""
    entries = list(
        VehicleEntry.objects.filter(is_trashed=False, no_plate=False, created_at__date=target_date)
    )
    payments = list(
        Payment.objects.filter(no_plate=False, created_at__date=target_date)
    )

    entries_by_plate = {}
    for e in entries:
        entries_by_plate.setdefault(_normalize_plate(e.plate), []).append(e)
    payments_by_plate = {}
    for p in payments:
        payments_by_plate.setdefault(_normalize_plate(p.plate), []).append(p)

    results = []

    for plate_key in set(entries_by_plate) | set(payments_by_plate):
        if plate_key == '':
            continue  # matrículas em branco tratadas em separado, mais abaixo

        seg_list = entries_by_plate.get(plate_key, [])
        tes_list = payments_by_plate.get(plate_key, [])

        candidates = []
        for e in seg_list:
            for p in tes_list:
                diff = abs(e.created_at - p.created_at)
                if diff <= MAX_MATCH_WINDOW:
                    same_service = e.service_id == p.service_id
                    candidates.append((0 if same_service else 1, diff, e, p))
        candidates.sort(key=lambda c: (c[0], c[1]))

        used_entries, used_payments = set(), set()
        for same_service_rank, _diff, e, p in candidates:
            if e.pk in used_entries or p.pk in used_payments:
                continue
            used_entries.add(e.pk)
            used_payments.add(p.pk)

            if same_service_rank != 0:
                results.append({'status': Reconciliation.Status.SERVICE_MISMATCH, 'entry': e, 'payment': p})
                continue

            expected = e.service.price_for(e.model) if e.service_id else None
            received = p.amount
            if expected is not None and expected != received:
                results.append({
                    'status': Reconciliation.Status.VALUE_MISMATCH, 'entry': e, 'payment': p,
                    'expected_value': expected, 'received_value': received,
                    'value_difference': expected - received,
                })
            else:
                results.append({'status': Reconciliation.Status.OK, 'entry': e, 'payment': p})

        for e in seg_list:
            if e.pk not in used_entries:
                results.append({'status': Reconciliation.Status.NO_PAYMENT, 'entry': e, 'payment': None})
        for p in tes_list:
            if p.pk not in used_payments:
                results.append({'status': Reconciliation.Status.NO_ENTRY, 'entry': None, 'payment': p})

    for e in entries_by_plate.get('', []):
        results.append({'status': Reconciliation.Status.UNVERIFIABLE, 'entry': e, 'payment': None})
    for p in payments_by_plate.get('', []):
        results.append({'status': Reconciliation.Status.UNVERIFIABLE, 'entry': None, 'payment': p})

    for e in VehicleEntry.objects.filter(is_trashed=False, no_plate=True, created_at__date=target_date):
        results.append({'status': Reconciliation.Status.UNVERIFIABLE, 'entry': e, 'payment': None})
    for p in Payment.objects.filter(no_plate=True, created_at__date=target_date):
        results.append({'status': Reconciliation.Status.UNVERIFIABLE, 'entry': None, 'payment': p})

    _persist_results(target_date, results)
    return Reconciliation.objects.filter(date=target_date).select_related(
        'vehicle_entry', 'payment', 'payment__service', 'vehicle_entry__service', 'reviewed_by'
    )


def _persist_results(target_date, results):
    existing = list(Reconciliation.objects.filter(date=target_date))
    reviewed = [r for r in existing if r.is_reviewed]
    reviewed_entry_ids = {r.vehicle_entry_id for r in reviewed if r.vehicle_entry_id}
    reviewed_payment_ids = {r.payment_id for r in reviewed if r.payment_id}

    Reconciliation.objects.filter(date=target_date).exclude(pk__in=[r.pk for r in reviewed]).delete()

    for item in results:
        entry = item.get('entry')
        payment = item.get('payment')
        if (entry and entry.pk in reviewed_entry_ids) or (payment and payment.pk in reviewed_payment_ids):
            continue
        Reconciliation.objects.create(
            date=target_date,
            vehicle_entry=entry,
            payment=payment,
            status=item['status'],
            expected_value=item.get('expected_value'),
            received_value=item.get('received_value'),
            value_difference=item.get('value_difference'),
        )
