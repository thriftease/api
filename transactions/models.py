from decimal import Decimal
from typing import Any

from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone

from accounts.models import Account


class Transaction(models.Model):
    def auto_now_add():  # type: ignore
        return timezone.now()

    account = models.ForeignKey(Account, models.CASCADE, default=None)
    amount = models.DecimalField(
        blank=True, max_digits=18, decimal_places=2, default=Decimal(0)
    )
    datetime = models.DateTimeField(blank=True, default=auto_now_add)
    name = models.CharField(blank=True, max_length=50, default="")
    description = models.TextField(blank=True, max_length=250, default="")

    tag_set: QuerySet[Any]

    @property
    def resulting_account_balance(self):
        return Account.get_balance_from_transactions(
            type(self).objects.filter(account=self.account, datetime__lte=self.datetime)
        )
