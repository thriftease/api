from django_filters import FilterSet

from users.models import User


class UserFilter(FilterSet):
    class Meta:
        model = User
        fields = {
            "id": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "given_name": ["exact", "icontains"],
            "middle_name": ["exact", "icontains"],
            "family_name": ["exact", "icontains"],
            "suffix": ["exact", "icontains"],
        }
