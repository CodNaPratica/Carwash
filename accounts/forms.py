from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.forms import PasswordInput, TextInput

from .models import User

CW_TEXT = {'class': 'form-control cw-form-input'}
CW_SELECT = {'class': 'form-select cw-form-input'}
CW_PASSWORD = {'class': 'form-control cw-form-input'}


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


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'role']
        labels = {'username': 'Nome de utilizador', 'first_name': 'Nome', 'last_name': 'Sobrenome', 'role': 'Perfil'}
        widgets = {
            'username': forms.TextInput(attrs=CW_TEXT),
            'first_name': forms.TextInput(attrs=CW_TEXT),
            'last_name': forms.TextInput(attrs=CW_TEXT),
            'role': forms.Select(attrs=CW_SELECT),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update(CW_PASSWORD)
        self.fields['password1'].label = 'Palavra-passe'
        self.fields['password2'].widget.attrs.update(CW_PASSWORD)
        self.fields['password2'].label = 'Confirmar palavra-passe'


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'role', 'is_active']
        labels = {
            'username': 'Nome de utilizador', 'first_name': 'Nome', 'last_name': 'Sobrenome',
            'role': 'Perfil', 'is_active': 'Ativo',
        }
        widgets = {
            'username': forms.TextInput(attrs=CW_TEXT),
            'first_name': forms.TextInput(attrs=CW_TEXT),
            'last_name': forms.TextInput(attrs=CW_TEXT),
            'role': forms.Select(attrs=CW_SELECT),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


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
