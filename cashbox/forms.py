from django import forms

from vehicles.forms import PlateValidationMixin, VehicleTypeFieldMixin

from .models import CashClosure, CashMovement, Payment


class PaymentForm(PlateValidationMixin, VehicleTypeFieldMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'brand', 'model', 'plate', 'no_plate', 'alt_identifier',
            'service', 'price_charged', 'amount', 'payment_method', 'notes',
        ]
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control cw-form-input'}),
            'plate': forms.TextInput(attrs={'class': 'form-control cw-form-input cw-plate-input'}),
            'no_plate': forms.CheckboxInput(attrs={'class': 'form-check-input cw-no-plate-toggle'}),
            'alt_identifier': forms.TextInput(attrs={'class': 'form-control cw-form-input'}),
            'service': forms.Select(attrs={'class': 'form-select cw-form-input'}),
            'price_charged': forms.NumberInput(attrs={'class': 'form-control cw-form-input', 'step': '0.01'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control cw-form-input', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-select cw-form-input'}),
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
