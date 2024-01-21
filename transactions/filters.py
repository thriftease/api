from transactions.models import Transaction
from utils.filter import OrFilterSet


class TransactionFilter(OrFilterSet):
    class Meta:
        model = Transaction
        fields = {
            "id": ["icontains"],
            "account__id": ["icontains"],
            "account__name": ["icontains"],
            "account__currency__name": ["icontains"],
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
            "tag__name": ["icontains"],
        }
