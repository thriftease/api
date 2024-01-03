from django.db.models import Q
from django_filters import FilterSet

from transactions.models import Transaction


class TransactionFilter(FilterSet):
    class Meta:
        model = Transaction
        fields = {
            "id": ["icontains"],
            "account__id": ["icontains"],
            "amount": ["icontains"],
            "datetime": [
                "icontains",
                "lt",
                "gt",
                "lte",
                "gte",
                "range",
                "year",
                "month",
                "day",
                "hour",
                "minute",
                "second",
            ],
            "name": ["icontains"],
            "description": ["icontains"],
        }

    @property
    def qs(self):
        qs = super().qs
        if self.data:
            expr = None
            for k, v in self.data.items():
                if v is None:
                    continue
                q = Q(**{k: v})
                expr = q if expr is None else expr | q
                qs = qs.filter(expr)
        return qs
