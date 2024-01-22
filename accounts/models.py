from decimal import Decimal

from django.db import models
from django.db.models import F, OuterRef
from django.db.models.query import QuerySet
from django.utils import timezone

from currencies.models import Currency
from transactions.models import Transaction


class AccountManager(models.Manager):
    def get_queryset(self):
        qs: QuerySet["Account"] = super().get_queryset()  # type: ignore
        ts = Transaction.objects  # type: ignore
        fields = dict(
            balance=(
                ts.values("new_account_balance")
                .filter(account_id=OuterRef("pk"), datetime__lte=timezone.now())
                .order_by("-datetime", "-id")[:1]
            ),
            future_balance=(
                ts.values("new_account_balance")
                .filter(account_id=OuterRef("pk"))
                .order_by("-datetime", "-id")[:1]
            ),
        )
        qs = qs.alias(**fields).annotate(**{k: F(k) for k in fields})
        return qs


class Account(models.Model):
    objects = AccountManager()

    currency = models.ForeignKey(Currency, models.CASCADE, default=None)
    name = models.CharField(max_length=50, default="")

    transaction_set: QuerySet[Transaction]

    class Meta:
        unique_together = (("currency", "name"),)

    balance = Decimal("0")
    future_balance = Decimal("0")

    # def get_balance(self, **filters):
    #     transaction = (
    #         self.transaction_set.filter(**filters).order_by("datetime", "id").last()
    #     )
    #     if transaction:
    #         return transaction.new_account_balance
    #     return Decimal("0.00")

    # @property
    # def balance(self):
    #     return self.get_balance(datetime__lte=timezone.now())

    # @property
    # def future_balance(self):
    #     return self.get_balance()
