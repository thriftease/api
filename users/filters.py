from django.db.models import Q
from django_filters import FilterSet

from users.models import User


class UserFilter(FilterSet):
    class Meta:
        model = User
        fields = {
            "id": ["icontains"],
            "email": ["icontains"],
            "given_name": ["icontains"],
            "middle_name": ["icontains"],
            "family_name": ["icontains"],
            "suffix": ["icontains"],
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
