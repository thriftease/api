from accounts.models import Account
from utils.filter import OrFilterSet


class AccountFilter(OrFilterSet):
    class Meta:
        model = Account
        fields = {
            "id": ["icontains"],
            "currency__id": ["icontains"],
            "name": ["icontains"],
        }
