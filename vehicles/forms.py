from django import forms

from .models import VehicleEntry

BOOTSTRAP_WIDGETS = {
    'brand': forms.TextInput(attrs={'class': 'form-control cw-form-input'}),
    'model': forms.TextInput(attrs={'class': 'form-control cw-form-input'}),
    'plate': forms.TextInput(attrs={'class': 'form-control cw-form-input'}),
    'photo': forms.ClearableFileInput(attrs={'class': 'form-control cw-form-input'}),
    'service': forms.Select(attrs={'class': 'form-select cw-form-input'}),
}


class VehicleEntryForm(forms.ModelForm):
    class Meta:
        model = VehicleEntry
        fields = ['brand', 'model', 'plate', 'photo', 'service']
        widgets = BOOTSTRAP_WIDGETS


class VehicleEntryEditForm(forms.ModelForm):
    reason = forms.CharField(
        label='Motivo da alteração',
        widget=forms.Textarea(attrs={'class': 'form-control cw-form-input', 'rows': 2}),
    )

    class Meta:
        model = VehicleEntry
        fields = ['brand', 'model', 'plate', 'photo', 'service']
        widgets = BOOTSTRAP_WIDGETS


class VehicleEntryTrashForm(forms.Form):
    reason = forms.CharField(
        label='Motivo para apagar',
        widget=forms.Textarea(attrs={'class': 'form-control cw-form-input', 'rows': 2}),
    )
