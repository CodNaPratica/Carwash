from django import forms

from .models import CashClosure, CashMovement, Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['vehicle_entry', 'service', 'amount', 'notes']
        labels = {
            'vehicle_entry': 'Carro',
            'service': 'Serviço',
            'amount': 'Valor recebido',
            'notes': 'Notas',
        }
        widgets = {
            'vehicle_entry': forms.Select(attrs={'class': 'form-select cw-form-input'}),
            'service': forms.Select(attrs={'class': 'form-select cw-form-input'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control cw-form-input', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control cw-form-input', 'rows': 2}),
        }


class CashMovementForm(forms.ModelForm):
    class Meta:
        model = CashMovement
        fields = ['category', 'amount', 'description', 'proof']
        labels = {
            'category': 'Categoria',
            'amount': 'Valor',
            'description': 'Descrição',
            'proof': 'Comprovativo',
        }
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select cw-form-input'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control cw-form-input', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control cw-form-input', 'rows': 2}),
            'proof': forms.ClearableFileInput(attrs={'class': 'form-control cw-form-input'}),
        }


class DailyClosureForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control cw-form-input', 'type': 'date'}))


class PeriodClosureForm(forms.Form):
    period_type = forms.ChoiceField(
        label='Tipo de período',
        choices=[
            (CashClosure.PeriodType.SEMANAL, 'Semanal'),
            (CashClosure.PeriodType.MENSAL, 'Mensal'),
        ],
        widget=forms.Select(attrs={'class': 'form-select cw-form-input'}),
    )
    date_start = forms.DateField(
        label='Data de início',
        widget=forms.DateInput(attrs={'class': 'form-control cw-form-input', 'type': 'date'}),
    )
    date_end = forms.DateField(
        label='Data de fim',
        widget=forms.DateInput(attrs={'class': 'form-control cw-form-input', 'type': 'date'}),
    )
    carried_forward = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False, initial=0,
        label='Valor a deixar no caixa (fundo de caixa)',
        widget=forms.NumberInput(attrs={'class': 'form-control cw-form-input', 'step': '0.01'}),
    )
