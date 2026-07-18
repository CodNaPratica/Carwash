from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SEGURANCA = 'seguranca', 'Segurança'
        TESOUREIRA = 'tesoureira', 'Tesoureira'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(max_length=20, choices=Role.choices)

    def is_seguranca(self):
        return self.role == self.Role.SEGURANCA

    def is_tesoureira(self):
        return self.role == self.Role.TESOUREIRA

    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser
