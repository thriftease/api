from django.db.models import Q
from django_filters import FilterSet

from tags.models import Tag


class TagFilter(FilterSet):
    class Meta:
        model = Tag
        fields = {
            "id": ["icontains"],
            "user__id": ["icontains"],
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
