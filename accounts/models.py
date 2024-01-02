from decimal import Decimal

from django.db import models

from currencies.models import Currency


class Account(models.Model):
    currency = models.ForeignKey(Currency, models.CASCADE, default=None)
    name = models.CharField(max_length=50, default="")

    @property
    def balance(self):
        return Decimal(0)
