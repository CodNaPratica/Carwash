from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import Permission
from django.forms import PasswordInput, TextInput

from .models import User

CW_TEXT = {'class': 'form-control cw-form-input'}
CW_SELECT = {'class': 'form-select cw-form-input'}
CW_PASSWORD = {'class': 'form-control cw-form-input'}

# Grouped as (section label, [(codename, label), ...]) - Django's own "grouped
# choices" format, renders with section headers via templates/widgets/permission_checkboxes.html.
# Only permissions actually checked somewhere by accounts.decorators.permission_required
# are listed here - no point offering a checkbox that gates nothing in the app.
PERMISSION_GROUPS = [
    ('Registos de Veículos', [
        ('vehicles.view_vehicleentry', 'Ver registos de veículos'),
        ('vehicles.add_vehicleentry', 'Registar veículos'),
        ('vehicles.change_vehicleentry', 'Editar registos (e marcar como concluído)'),
        ('vehicles.delete_vehicleentry', 'Apagar registos (mover para o lixo)'),
        ('vehicles.manage_trash', 'Gerir o lixo (restaurar / apagar definitivo)'),
        ('vehicles.add_vehicletype', 'Criar tipos de veículo'),
        ('vehicles.change_vehicletype', 'Aprovar tipos de veículo'),
        ('vehicles.delete_vehicletype', 'Apagar tipos de veículo'),
    ]),
    ('Caixa', [
        ('cashbox.view_payment', 'Ver pagamentos'),
        ('cashbox.add_payment', 'Registar pagamentos'),
        ('cashbox.add_cashmovement', 'Registar custos/despesas'),
        ('cashbox.add_cashclosure', 'Fechar caixa diário'),
        ('cashbox.view_cashclosure', 'Ver fechamentos'),
        ('cashbox.close_period', 'Fechar período semanal/mensal'),
    ]),
    ('Serviços', [
        ('services.view_service', 'Ver serviços'),
        ('services.add_service', 'Criar serviços'),
        ('services.change_service', 'Editar serviços e preços'),
    ]),
    ('Conferência (Auditoria)', [
        ('audit.view_reconciliation', 'Ver Conferência de Registos'),
        ('audit.change_reconciliation', 'Investigar / atualizar casos'),
        ('audit.add_reconciliation', 'Ligar registos manualmente'),
    ]),
    ('Sistema', [
        ('accounts.view_admin_dashboard', 'Ver dashboard administrativo'),
        ('accounts.view_user', 'Ver utilizadores'),
        ('accounts.add_user', 'Criar utilizadores'),
        ('accounts.change_user', 'Editar utilizadores / redefinir password'),
    ]),
]


class GroupedCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = 'widgets/permission_checkboxes.html'


class UserPermissionsFieldMixin:
    """Renders a "Permissões" checklist instead of a "Perfil" dropdown -
    access is granted permission by permission, not by picking a pre-made
    role. Saving sets these as the user's direct permissions and clears any
    Group membership, so the checklist is always the one source of truth
    (editing an existing group-based user migrates them to direct permissions
    automatically, without changing what they can actually do)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permissions'] = forms.MultipleChoiceField(
            choices=PERMISSION_GROUPS, required=False, label='Permissões',
            widget=GroupedCheckboxSelectMultiple,
        )
        if self.instance and self.instance.pk:
            self.initial['permissions'] = sorted(self.instance.get_all_permissions())

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            self._assign_permissions(user)
        return user

    def _assign_permissions(self, user):
        perms = []
        for value in self.cleaned_data.get('permissions', []):
            app_label, codename = value.split('.', 1)
            perm = Permission.objects.filter(content_type__app_label=app_label, codename=codename).first()
            if perm:
                perms.append(perm)
        user.user_permissions.set(perms)
        user.groups.clear()


class BootstrapAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(
        label='Lembrar-me', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = TextInput(attrs={'class': 'form-control'})
        self.fields['password'].widget = PasswordInput(attrs={'class': 'form-control'})
        self.order_fields(['username', 'password', 'remember_me'])


class UserCreateForm(UserPermissionsFieldMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']
        labels = {'username': 'Nome de utilizador', 'first_name': 'Nome', 'last_name': 'Sobrenome'}
        widgets = {
            'username': forms.TextInput(attrs=CW_TEXT),
            'first_name': forms.TextInput(attrs=CW_TEXT),
            'last_name': forms.TextInput(attrs=CW_TEXT),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update(CW_PASSWORD)
        self.fields['password1'].label = 'Palavra-passe'
        self.fields['password2'].widget.attrs.update(CW_PASSWORD)
        self.fields['password2'].label = 'Confirmar palavra-passe'
        self.order_fields(['username', 'first_name', 'last_name', 'permissions', 'password1', 'password2'])


class UserEditForm(UserPermissionsFieldMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'is_active']
        labels = {
            'username': 'Nome de utilizador', 'first_name': 'Nome', 'last_name': 'Sobrenome',
            'is_active': 'Ativo',
        }
        widgets = {
            'username': forms.TextInput(attrs=CW_TEXT),
            'first_name': forms.TextInput(attrs=CW_TEXT),
            'last_name': forms.TextInput(attrs=CW_TEXT),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['username', 'first_name', 'last_name', 'is_active', 'permissions'])


class SetPasswordForm(forms.Form):
    new_password = forms.CharField(
        label='Nova palavra-passe', min_length=8,
        widget=forms.PasswordInput(attrs=CW_PASSWORD),
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {'first_name': 'Nome', 'last_name': 'Sobrenome', 'email': 'Email'}
        widgets = {
            'first_name': forms.TextInput(attrs=CW_TEXT),
            'last_name': forms.TextInput(attrs=CW_TEXT),
            'email': forms.EmailInput(attrs=CW_TEXT),
        }


class CwPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update(CW_PASSWORD)
        self.fields['old_password'].label = 'Palavra-passe atual'
        self.fields['new_password1'].widget.attrs.update(CW_PASSWORD)
        self.fields['new_password1'].label = 'Nova palavra-passe'
        self.fields['new_password2'].widget.attrs.update(CW_PASSWORD)
        self.fields['new_password2'].label = 'Confirmar nova palavra-passe'
