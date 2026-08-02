from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Meta:
        permissions = [
            ('view_admin_dashboard', 'Pode ver o dashboard administrativo'),
        ]

    def is_seguranca(self):
        return self.has_perm('vehicles.view_vehicleentry')

    def is_tesoureira(self):
        return self.has_perm('cashbox.view_payment')

    def is_admin_role(self):
        return self.is_superuser or self.has_perm('accounts.view_admin_dashboard')

    @property
    def role_label(self):
        if self.is_admin_role():
            return 'Admin'
        labels = []
        if self.is_seguranca():
            labels.append('Operador de Registo')
        if self.is_tesoureira():
            labels.append('Caixa')
        return ' + '.join(labels) if labels else 'Sem perfil'
