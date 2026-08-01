from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    def is_seguranca(self):
        return self.groups.filter(name='Operador de Registo').exists()

    def is_tesoureira(self):
        return self.groups.filter(name='Caixa').exists()

    def is_admin_role(self):
        return self.is_superuser or self.groups.filter(name='Admin').exists()

    @property
    def role_label(self):
        if self.is_admin_role():
            return 'Admin'
        group = self.groups.order_by('name').first()
        return group.name if group else 'Sem perfil'
