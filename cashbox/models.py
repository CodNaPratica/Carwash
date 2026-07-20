from django.conf import settings
from django.db import models

from services.models import Service
from vehicles.models import VehicleEntry, VehicleType


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        DINHEIRO = 'dinheiro', 'Dinheiro'
        MPESA_EMOLA = 'mpesa_emola', 'M-Pesa / e-Mola'

    # Ligação antiga por FK - mantida só por compatibilidade com dados já existentes.
    # O formulário novo já não a usa: a tesoureira regista marca/modelo/matrícula
    # de forma independente do registo do segurança (ver app `audit` para o cruzamento).
    vehicle_entry = models.ForeignKey(
        VehicleEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments'
    )

    brand = models.CharField('Marca', max_length=50, default='')
    model = models.ForeignKey(
        VehicleType, verbose_name='Tipo de Veículo', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='payments_new'
    )
    plate = models.CharField('Matrícula', max_length=20, blank=True)
    no_plate = models.BooleanField('Sem matrícula', default=False)

    service = models.ForeignKey(Service, verbose_name='Serviço', on_delete=models.PROTECT)
    price_charged = models.DecimalField('Valor cobrado', max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField('Valor recebido', max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        'Forma de pagamento', max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.DINHEIRO
    )

    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    notes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Pagamento {self.amount} - {self.created_at:%Y-%m-%d}'


class CashMovement(models.Model):
    class Category(models.TextChoices):
        CUSTO = 'custo', 'Custo'
        DESPESA = 'despesa', 'Despesa'

    category = models.CharField(max_length=20, choices=Category.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    proof = models.FileField(upload_to='proofs/')
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_category_display()} {self.amount} - {self.created_at:%Y-%m-%d}'


class CashClosure(models.Model):
    class PeriodType(models.TextChoices):
        DIARIO = 'diario', 'Diário'
        SEMANAL = 'semanal', 'Semanal'
        MENSAL = 'mensal', 'Mensal'

    period_type = models.CharField(max_length=20, choices=PeriodType.choices)
    date_start = models.DateField()
    date_end = models.DateField()
    total_in = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_out = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    carried_forward = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    closed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_end']
        constraints = [
            models.UniqueConstraint(
                fields=['period_type', 'date_start', 'date_end'], name='unique_closure_period'
            )
        ]

    def __str__(self):
        return f'Fecho {self.get_period_type_display()} {self.date_start} a {self.date_end}'
