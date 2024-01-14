from django.db.models import Q
from django_filters import FilterSet

from currencies.models import Currency


class CurrencyFilter(FilterSet):
    class Meta:
        model = Currency
        fields = {
            "id": ["icontains"],
            "user__id": ["icontains"],
            "abbreviation": ["exact", "icontains"],
            "symbol": ["icontains"],
            "name": ["icontains"],
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
