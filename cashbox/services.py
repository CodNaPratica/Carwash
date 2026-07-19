from django.db.models import Sum
from django.utils import timezone

from .models import CashClosure, CashMovement, Payment


def get_unclosed_previous_day():
    """Devolve a data mais antiga, anterior a hoje, com movimentos sem fecho diário. None se não houver."""
    today = timezone.localdate()
    payment_dates = set(
        Payment.objects.filter(created_at__date__lt=today).values_list('created_at__date', flat=True)
    )
    movement_dates = set(
        CashMovement.objects.filter(created_at__date__lt=today).values_list('created_at__date', flat=True)
    )
    dates = payment_dates | movement_dates
    closed_dates = set(
        CashClosure.objects.filter(period_type=CashClosure.PeriodType.DIARIO).values_list('date_start', flat=True)
    )
    unclosed = sorted(d for d in dates if d not in closed_dates)
    return unclosed[0] if unclosed else None


def totals_for_range(date_start, date_end):
    total_in = Payment.objects.filter(
        created_at__date__gte=date_start, created_at__date__lte=date_end
    ).aggregate(total=Sum('amount'))['total'] or 0
    total_out = CashMovement.objects.filter(
        created_at__date__gte=date_start, created_at__date__lte=date_end
    ).aggregate(total=Sum('amount'))['total'] or 0
    return total_in, total_out


def movement_breakdown(date_start, date_end):
    """Devolve (total_custo, total_despesa) para o período - as duas categorias de saída."""
    qs = CashMovement.objects.filter(created_at__date__gte=date_start, created_at__date__lte=date_end)
    total_custo = qs.filter(category=CashMovement.Category.CUSTO).aggregate(total=Sum('amount'))['total'] or 0
    total_despesa = qs.filter(category=CashMovement.Category.DESPESA).aggregate(total=Sum('amount'))['total'] or 0
    return total_custo, total_despesa


def last_closure(period_type):
    return CashClosure.objects.filter(period_type=period_type).order_by('-date_end').first()
