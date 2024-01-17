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

    class Meta:
        unique_together = (("currency", "name"),)

    @classmethod
    def get_balance_from_transactions(cls, transaction_set: QuerySet[Any]):
        transactions = transaction_set.order_by("datetime", "id")
        if transactions:
            amounts = map(lambda e: Decimal(e.amount), transactions)
            return sum(amounts)
        return Decimal(0)

    def get_balance(self, **filters):
        return self.get_balance_from_transactions(
            self.transaction_set.filter(**filters)
        )

    @property
    def balance(self):
        return self.get_balance(datetime__lte=timezone.now())

    @property
    def future_balance(self):
        return self.get_balance()
