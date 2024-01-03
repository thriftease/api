from django.db import models

from transactions.models import Transaction
from users.models import User


class Tag(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    name = models.CharField(max_length=50, default="")
    transaction_set = models.ManyToManyField(Transaction)

    class Meta:
        unique_together = (("user", "name"),)
