from django.conf import settings
from django.db import models

from cashbox.models import Payment
from vehicles.models import VehicleEntry


class Reconciliation(models.Model):
    class Status(models.TextChoices):
        OK = 'ok', 'Conferem'
        SERVICE_MISMATCH = 'service_mismatch', 'Divergência de serviço'
        VALUE_MISMATCH = 'value_mismatch', 'Divergência de valor'
        NO_PAYMENT = 'no_payment', 'Sem pagamento'
        NO_ENTRY = 'no_entry', 'Sem registo de entrada'
        UNVERIFIABLE = 'unverifiable', 'Não verificável'

    class Investigation(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        RESOLVIDO = 'resolvido', 'Resolvido'
        JUSTIFICADO = 'justificado', 'Justificado'
        FRAUDE = 'fraude', 'Fraude confirmada'

    date = models.DateField()
    vehicle_entry = models.ForeignKey(
        VehicleEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='reconciliations'
    )
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='reconciliations'
    )
    status = models.CharField(max_length=20, choices=Status.choices)

    expected_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    received_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    value_difference = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    investigation_status = models.CharField(
        max_length=20, choices=Investigation.choices, default=Investigation.PENDENTE
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'status']

    def __str__(self):
        return f'{self.date} - {self.get_status_display()}'

    @property
    def is_reviewed(self):
        return self.investigation_status != self.Investigation.PENDENTE or bool(self.review_note)
