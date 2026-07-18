from django.db import models


class Service(models.Model):
    name = models.CharField('Nome', max_length=100)
    price = models.DecimalField('Preço', max_digits=10, decimal_places=2)
    active = models.BooleanField('Ativo', default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.price})'
