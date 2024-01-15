from currencies.models import Currency
from utils.filter import OrFilterSet


class CurrencyFilter(OrFilterSet):
    class Meta:
        model = Currency
        fields = {
            "id": ["icontains"],
            "user__id": ["icontains"],
            "abbreviation": ["iexact", "icontains"],
            "symbol": ["icontains"],
            "name": ["icontains"],
        }
