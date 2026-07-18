from django import forms

from .models import Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price', 'active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control cw-form-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-control cw-form-input', 'step': '0.01'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ServiceQuickForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price']
