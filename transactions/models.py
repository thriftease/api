from decimal import Decimal
from enum import StrEnum
from typing import Any, Self

from django.db import models
from django.db.models import Q
from django.db.models.manager import BaseManager
from django.db.models.query import QuerySet
from django.utils import timezone


class TransactionOperation(StrEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class Transaction(models.Model):
    def auto_now_add():  # type: ignore
        return timezone.now()

    account = models.ForeignKey("accounts.Account", models.CASCADE, default=None)
    amount = models.DecimalField(
        blank=True, max_digits=18, decimal_places=2, default=Decimal(0)
    )
    datetime = models.DateTimeField(blank=True, default=auto_now_add)
    name = models.CharField(blank=True, max_length=50, default="")
    description = models.TextField(blank=True, max_length=250, default="")

    tag_set: QuerySet[Any]

    @classmethod
    def sum(cls, transaction_set: BaseManager[Self]):
        transactions = transaction_set.order_by("datetime", "id")
        if transactions:
            amounts = map(lambda e: Decimal(e.amount), transactions)
            return sum(amounts)
        return Decimal("0.00")

    @property
    def new_account_balance(self):
        return self.old_account_balance + Decimal(self.amount)

    @property
    def old_account_balance(self):
        transactions = type(self).objects.filter(
            (
                Q(datetime__lt=self.datetime)
                | (Q(datetime=self.datetime) & ~Q(pk=self.pk) & Q(pk__lt=self.pk))
            ),
            account=self.account,
        )
        return self.sum(transactions)

    @property
    def scheduled(self):
        return self.datetime > timezone.now()

    @property
    def operation(self) -> TransactionOperation:
        return (
            TransactionOperation.DEBIT
            if Decimal(self.amount) < 0
            else TransactionOperation.CREDIT
        )
