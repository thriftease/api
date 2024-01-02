from decimal import Decimal
from typing import Any

from django.db import models
from django.db.models.query import QuerySet

from currencies.models import Currency


class Account(models.Model):
    currency = models.ForeignKey(Currency, models.CASCADE, default=None)
    name = models.CharField(max_length=50, default="")

    transaction_set: QuerySet[Any]

    @property
    def balance(self):
        transactions = self.transaction_set.order_by("datetime", "id")
        if transactions:
            amounts = map(lambda e: Decimal(e.amount), transactions)
            return sum(amounts)
        return Decimal(0)
