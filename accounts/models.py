from decimal import Decimal

from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone

from currencies.models import Currency
from transactions.models import Transaction


class Account(models.Model):
    currency = models.ForeignKey(Currency, models.CASCADE, default=None)
    name = models.CharField(max_length=50, default="")

    transaction_set: QuerySet[Transaction]

    class Meta:
        unique_together = (("currency", "name"),)

    def get_balance(self, **filters):
        transaction = (
            self.transaction_set.filter(**filters).order_by("datetime", "id").last()
        )
        if transaction:
            return transaction.new_account_balance
        return Decimal("0.00")

    @property
    def balance(self):
        return self.get_balance(datetime__lte=timezone.now())

    @property
    def future_balance(self):
        return self.get_balance()
