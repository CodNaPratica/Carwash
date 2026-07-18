from django.conf import settings
from django.db import models

from services.models import Service


class VehicleEntry(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        ADOTADO = 'adotado', 'Adotado'
        CONCLUIDO = 'concluido', 'Concluído'

    brand = models.CharField('Marca', max_length=50)
    model = models.CharField('Modelo', max_length=50)
    plate = models.CharField('Matrícula', max_length=20)
    photo = models.ImageField('Foto', upload_to='vehicles/', blank=True, null=True)
    service = models.ForeignKey(
        Service, verbose_name='Serviço', on_delete=models.SET_NULL, null=True, blank=True
    )

    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='vehicle_entries_registered'
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDENTE)

    claimed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='vehicle_entries_claimed'
    )
    claimed_at = models.DateTimeField(null=True, blank=True)

    is_trashed = models.BooleanField(default=False)
    trash_reason = models.TextField(blank=True)
    trashed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='vehicle_entries_trashed'
    )
    trashed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Vehicle entries'

    def __str__(self):
        return f'{self.brand} {self.model} - {self.plate}'


class VehicleEntryLog(models.Model):
    entry = models.ForeignKey(VehicleEntry, on_delete=models.CASCADE, related_name='logs')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    reason = models.TextField()
    snapshot = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Log {self.entry_id} @ {self.created_at:%Y-%m-%d %H:%M}'
