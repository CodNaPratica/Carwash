from django.conf import settings
from django.db import models

from services.models import Service


class VehicleType(models.Model):
    name = models.CharField('Tipo de veículo', max_length=50, unique=True)
    is_approved = models.BooleanField('Aprovado', default=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Adicionado por', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='vehicle_types_added'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class VehicleEntry(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        ADOTADO = 'adotado', 'Adotado'
        CONCLUIDO = 'concluido', 'Concluído'

    brand = models.CharField('Marca', max_length=50)
    model = models.ForeignKey(
        VehicleType, verbose_name='Tipo de Veículo', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='vehicle_entries'
    )
    plate = models.CharField('Matrícula', max_length=20, blank=True)
    no_plate = models.BooleanField('Sem matrícula', default=False)
    alt_identifier = models.CharField('Chassis / Descrição', max_length=100, blank=True)
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
        if self.plate:
            return f'{self.brand} {self.model} - {self.plate}'
        if self.no_plate and self.alt_identifier:
            return f'{self.brand} {self.model} - {self.alt_identifier}'
        return f'{self.brand} {self.model}'


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
