from datetime import datetime

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone

from accounts.decorators import role_required

from .forms import CashMovementForm, PaymentForm, PeriodClosureForm
from .models import CashClosure, CashMovement, Payment
from .services import get_unclosed_previous_day, last_closure, movement_breakdown, totals_for_range


def _dashboard_context(user, **overrides):
    today = timezone.localdate()
    unclosed_day = get_unclosed_previous_day()
    total_in, total_out = totals_for_range(today, today)
    total_custo, total_despesa = movement_breakdown(today, today)
    unclosed_total_in = unclosed_total_out = None
    if unclosed_day:
        unclosed_total_in, unclosed_total_out = totals_for_range(unclosed_day, unclosed_day)

    context = {
        'today': today,
        'unclosed_day': unclosed_day,
        'unclosed_total_in': unclosed_total_in,
        'unclosed_total_out': unclosed_total_out,
        'unclosed_balance': (unclosed_total_in - unclosed_total_out) if unclosed_day else None,
        'total_in': total_in,
        'total_out': total_out,
        'total_custo': total_custo,
        'total_despesa': total_despesa,
        'balance': total_in - total_out,
        'payments': Payment.objects.filter(created_at__date=today),
        'movements': CashMovement.objects.filter(created_at__date=today),
        'today_closed': CashClosure.objects.filter(
            period_type=CashClosure.PeriodType.DIARIO, date_start=today
        ).exists(),
        'payment_form': PaymentForm(user=user),
        'movement_form': CashMovementForm(),
        'open_payment_modal': False,
        'open_movement_modal': False,
    }
    context.update(overrides)
    return context


@role_required('tesoureira')
def home(request):
    today = timezone.localdate()
    total_in, total_out = totals_for_range(today, today)
    total_custo, total_despesa = movement_breakdown(today, today)
    return render(request, 'cashbox/home.html', {
        'total_in': total_in,
        'total_out': total_out,
        'total_custo': total_custo,
        'total_despesa': total_despesa,
        'balance': total_in - total_out,
        'payments': Payment.objects.filter(created_at__date=today),
        'movements': CashMovement.objects.filter(created_at__date=today),
    })


@role_required('tesoureira')
def dashboard(request):
    open_param = request.GET.get('open')
    overrides = {}
    if open_param == 'payment':
        overrides['open_payment_modal'] = True
    elif open_param == 'movement':
        overrides['open_movement_modal'] = True
    return render(request, 'cashbox/dashboard.html', _dashboard_context(request.user, **overrides))


@role_required('tesoureira')
def payment_create(request):
    unclosed_day = get_unclosed_previous_day()
    if unclosed_day:
        messages.error(request, f'Feche primeiro o caixa do dia {unclosed_day} antes de registar novos valores.')
        return redirect('cashbox:dashboard')
    if request.method == 'POST':
        form = PaymentForm(request.POST, user=request.user)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.received_by = request.user
            payment.save()
            messages.success(request, 'Pagamento registado.')
            return redirect('cashbox:dashboard')
        return render(request, 'cashbox/dashboard.html', _dashboard_context(request.user, payment_form=form, open_payment_modal=True))
    return redirect('cashbox:dashboard')


@role_required('tesoureira')
def movement_create(request):
    unclosed_day = get_unclosed_previous_day()
    if unclosed_day:
        messages.error(request, f'Feche primeiro o caixa do dia {unclosed_day} antes de registar novos valores.')
        return redirect('cashbox:dashboard')
    if request.method == 'POST':
        form = CashMovementForm(request.POST, request.FILES)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.registered_by = request.user
            movement.save()
            messages.success(request, 'Movimento registado.')
            return redirect('cashbox:dashboard')
        return render(request, 'cashbox/dashboard.html', _dashboard_context(request.user, movement_form=form, open_movement_modal=True))
    return redirect('cashbox:dashboard')


@role_required('tesoureira')
def daily_closure(request, date):
    date = datetime.strptime(date, '%Y-%m-%d').date()
    if request.method != 'POST':
        return redirect('cashbox:dashboard')
    if CashClosure.objects.filter(period_type=CashClosure.PeriodType.DIARIO, date_start=date).exists():
        messages.info(request, 'Este dia já está fechado.')
        return redirect('cashbox:dashboard')
    total_in, total_out = totals_for_range(date, date)
    CashClosure.objects.create(
        period_type=CashClosure.PeriodType.DIARIO,
        date_start=date, date_end=date,
        total_in=total_in, total_out=total_out,
        balance=total_in - total_out,
        closed_by=request.user,
    )
    messages.success(request, f'Caixa do dia {date} fechado.')
    return redirect('cashbox:dashboard')


@role_required('admin')
def closures(request):
    closure_list = CashClosure.objects.all()
    return render(request, 'cashbox/closures.html', {
        'closures': closure_list,
        'period_form': PeriodClosureForm(),
        'open_period_modal': False,
    })


@role_required('admin')
def period_closure_create(request):
    if request.method == 'POST':
        form = PeriodClosureForm(request.POST)
        if form.is_valid():
            period_type = form.cleaned_data['period_type']
            date_start = form.cleaned_data['date_start']
            date_end = form.cleaned_data['date_end']
            carried_forward = form.cleaned_data['carried_forward'] or 0

            previous = last_closure(period_type)
            if previous and date_start <= previous.date_end:
                messages.error(
                    request,
                    f'Já existe um fecho {previous.get_period_type_display()} até {previous.date_end}. '
                    'Escolha um período posterior.',
                )
                return render(request, 'cashbox/closures.html', {
                    'closures': CashClosure.objects.all(),
                    'period_form': form,
                    'open_period_modal': True,
                })

            total_in, total_out = totals_for_range(date_start, date_end)
            CashClosure.objects.create(
                period_type=period_type, date_start=date_start, date_end=date_end,
                total_in=total_in, total_out=total_out, balance=total_in - total_out,
                carried_forward=carried_forward, closed_by=request.user,
            )
            messages.success(request, 'Fecho de caixa criado.')
            return redirect('cashbox:closures')
        return render(request, 'cashbox/closures.html', {
            'closures': CashClosure.objects.all(),
            'period_form': form,
            'open_period_modal': True,
        })
    return redirect('cashbox:closures')
