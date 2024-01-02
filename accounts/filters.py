from django.db.models import Q
from django_filters import FilterSet

from accounts.models import Account


class AccountFilter(FilterSet):
    class Meta:
        model = Account
        fields = {
            "id": ["icontains"],
            "currency__id": ["icontains"],
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
