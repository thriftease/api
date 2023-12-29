from django.db import models

from users.models import User


class Currency(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    abbreviation = models.CharField(max_length=15, default="")
    symbol = models.CharField(max_length=15, default="")
    name = models.CharField(max_length=50, default="")

    class Meta:
        unique_together = (("user", "abbreviation"),)

    def save(self, *args, **kwargs):
        if self.abbreviation:
            self.abbreviation = self.abbreviation.lower()
        return super().save(*args, **kwargs)
