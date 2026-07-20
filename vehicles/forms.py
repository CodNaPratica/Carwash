from django import forms
from django.db.models import Q

from .models import VehicleEntry, VehicleType

BOOTSTRAP_WIDGETS = {
    'brand': forms.TextInput(attrs={'class': 'form-control cw-form-input'}),
    'plate': forms.TextInput(attrs={'class': 'form-control cw-form-input cw-plate-input'}),
    'no_plate': forms.CheckboxInput(attrs={'class': 'form-check-input cw-no-plate-toggle'}),
    'photo': forms.ClearableFileInput(attrs={'class': 'form-control cw-form-input'}),
    'service': forms.Select(attrs={'class': 'form-select cw-form-input'}),
}

VEHICLE_TYPE_CUSTOM_VALUE = '__custom__'


class VehicleTypeFieldMixin:
    """Renders the `model` FK (VehicleType) as a dropdown built from the DB
    instead of Django's default ModelChoiceField, so a "Outro" option can
    reveal a free-text input (see cw-model-select JS in base.html). Typing a
    new name there creates a VehicleType with is_approved=False, pending
    admin review in the "Tipos de Veículo" page - it's usable immediately by
    whoever added it, it just isn't offered to everyone else until approved.
    """

    def __init__(self, *args, **kwargs):
        self._vt_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        is_admin = bool(self._vt_user and self._vt_user.is_admin_role())
        if is_admin:
            queryset = VehicleType.objects.all()
        elif self._vt_user:
            queryset = VehicleType.objects.filter(Q(is_approved=True) | Q(added_by=self._vt_user))
        else:
            queryset = VehicleType.objects.filter(is_approved=True)

        current_pk = getattr(self.instance, 'model_id', None)
        choices = [('', 'Selecione o tipo de veículo')]
        seen_pks = set()
        for vt in queryset.distinct().order_by('name'):
            label = vt.name if (vt.is_approved or is_admin is False) else f'{vt.name} (pendente)'
            choices.append((str(vt.pk), label))
            seen_pks.add(vt.pk)
        if current_pk and current_pk not in seen_pks:
            choices.append((str(current_pk), self.instance.model.name))
        choices.append((VEHICLE_TYPE_CUSTOM_VALUE, 'Outro (especificar)'))

        self.fields['model'] = forms.CharField(
            label='Tipo de Veículo',
            widget=forms.Select(choices=choices, attrs={'class': 'form-select cw-form-input cw-model-select'}),
        )
        if current_pk:
            self.initial['model'] = str(current_pk)

    def clean_model(self):
        value = (self.cleaned_data.get('model') or '').strip()
        if not value:
            raise forms.ValidationError('Selecione ou adicione o tipo de veículo.')
        if value == VEHICLE_TYPE_CUSTOM_VALUE:
            raise forms.ValidationError('Especifique o tipo de veículo.')
        if value.isdigit():
            try:
                return VehicleType.objects.get(pk=int(value))
            except VehicleType.DoesNotExist:
                pass
        existing = VehicleType.objects.filter(name__iexact=value).first()
        if existing:
            return existing
        return VehicleType.objects.create(name=value, is_approved=False, added_by=self._vt_user)


class VehicleTypeForm(forms.ModelForm):
    class Meta:
        model = VehicleType
        fields = ['name', 'is_approved']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control cw-form-input'}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PlateValidationMixin:
    def clean(self):
        cleaned_data = super().clean()
        no_plate = cleaned_data.get('no_plate')
        plate = cleaned_data.get('plate')

        if not no_plate and not plate:
            self.add_error('plate', 'A matrícula é obrigatória, a menos que marque "Sem matrícula".')

        return cleaned_data


class VehicleEntryForm(PlateValidationMixin, VehicleTypeFieldMixin, forms.ModelForm):
    class Meta:
        model = VehicleEntry
        fields = ['brand', 'model', 'plate', 'no_plate', 'photo', 'service']
        widgets = BOOTSTRAP_WIDGETS


class VehicleEntryEditForm(PlateValidationMixin, VehicleTypeFieldMixin, forms.ModelForm):
    reason = forms.CharField(
        label='Motivo da alteração',
        widget=forms.Textarea(attrs={'class': 'form-control cw-form-input', 'rows': 2}),
    )

    class Meta:
        model = VehicleEntry
        fields = ['brand', 'model', 'plate', 'no_plate', 'photo', 'service']
        widgets = BOOTSTRAP_WIDGETS


class VehicleEntryTrashForm(forms.Form):
    reason = forms.CharField(
        label='Motivo para apagar',
        widget=forms.Textarea(attrs={'class': 'form-control cw-form-input', 'rows': 2}),
    )
