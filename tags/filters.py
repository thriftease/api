from tags.models import Tag
from utils.filter import OrFilterSet


class TagFilter(OrFilterSet):
    class Meta:
        model = Tag
        fields = {
            "id": ["icontains"],
            "user__id": ["icontains"],
            "name": ["icontains"],
        }
