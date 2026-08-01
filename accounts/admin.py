from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Perfis (Operador de Registo/Caixa/Admin) são geridos via Grupos - já
    incluídos por omissão em UserAdmin.fieldsets, sem precisar de nada extra."""
    list_display = ('username', 'email', 'is_staff', 'is_active')
