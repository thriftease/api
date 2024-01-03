from decimal import Decimal
from typing import Any

from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone

from currencies.models import Currency


class Account(models.Model):
    currency = models.ForeignKey(Currency, models.CASCADE, default=None)
    name = models.CharField(max_length=50, default="")

    transaction_set: QuerySet[Any]

    def get_balance(self, **filters):
        transactions = self.transaction_set.filter(**filters).order_by("datetime", "id")
        if transactions:
            amounts = map(lambda e: Decimal(e.amount), transactions)
            return sum(amounts)
        return Decimal(0)

    @property
    def balance(self):
        return self.get_balance(datetime__lte=timezone.now())

    @property
    def future_balance(self):
        return self.get_balance()
