from django.db import models


class Service(models.Model):
    name = models.CharField('Nome', max_length=100)
    price = models.DecimalField('Preço base', max_digits=10, decimal_places=2)
    active = models.BooleanField('Ativo', default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.price})'

    def price_for(self, vehicle_type):
        """Preço específico para o tipo de veículo, se definido em ServicePrice;
        caso contrário, cai para o preço base do serviço."""
        if vehicle_type is None:
            return self.price
        override = self.prices.filter(vehicle_type=vehicle_type).first()
        return override.price if override else self.price


class ServicePrice(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='prices')
    vehicle_type = models.ForeignKey(
        'vehicles.VehicleType', verbose_name='Tipo de Veículo', on_delete=models.CASCADE, related_name='service_prices'
    )
    price = models.DecimalField('Preço', max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['service__name', 'vehicle_type__name']
        constraints = [
            models.UniqueConstraint(fields=['service', 'vehicle_type'], name='unique_service_vehicle_price')
        ]

    def __str__(self):
        return f'{self.service.name} - {self.vehicle_type.name}: {self.price}'
