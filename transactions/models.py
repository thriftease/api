from decimal import Decimal
from enum import StrEnum
from typing import Any

from django.db import models
from django.db.models import Case, F, OuterRef, Q, Sum, Value, When
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from django.utils import timezone


class TransactionOperation(StrEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class TransactionManager(models.Manager):
    def get_queryset(self):
        qs: QuerySet["Transaction"] = super().get_queryset()  # type: ignore
        fields = dict(
            old_account_balance=Coalesce(
                (
                    qs.values(sum=Sum("amount"))
                    .filter(
                        (
                            Q(datetime__lt=OuterRef("datetime"))
                            | (
                                Q(datetime=OuterRef("datetime"))
                                & ~Q(pk=OuterRef("pk"))
                                & Q(pk__lt=OuterRef("pk"))
                            )
                        ),
                        account=OuterRef("account"),
                    )
                    .order_by("datetime", "id")
                ),
                Decimal("0"),
            ),
            new_account_balance=F("old_account_balance") + F("amount"),
            scheduled=Case(
                When(datetime__gt=timezone.now(), then=True),
                default=False,
            ),
            operation=Case(
                When(
                    amount__lt=Decimal("0"),
                    then=Value(TransactionOperation.DEBIT.value),
                ),
                default=Value(TransactionOperation.CREDIT.value),
            ),
        )
        qs = qs.alias(**fields).annotate(**{k: F(k) for k in fields})
        return qs


class Transaction(models.Model):
    objects = TransactionManager()

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

    old_account_balance = Decimal("0")
    new_account_balance = Decimal("0")
    scheduled = False
    operation = TransactionOperation = TransactionOperation.CREDIT
