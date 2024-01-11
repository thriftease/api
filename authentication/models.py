import base64

from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone

from users.models import User


class AuthReset(models.Model):
    user = models.OneToOneField(
        User, default=None, on_delete=models.CASCADE, unique=True
    )
    token = models.CharField(max_length=255, null=False, blank=False)
    datetime = models.DateTimeField(auto_now_add=True)

    @property
    def expired(self):
        # Calculate the time difference between now and the created_at time
        time_difference = timezone.now() - self.datetime
        # Define the threshold duration (5 minutes in this case)
        threshold_duration = timezone.timedelta(minutes=5)
        # Check if the time difference exceeds the threshold duration
        return time_difference >= threshold_duration

    def encode(self):
        token = self.token
        token_bytes = token.encode("ascii")
        return base64.b64encode(token_bytes).decode("ascii")

    @classmethod
    def decode(cls, base64_token: str):
        base64_bytes = base64_token.encode("ascii")
        decoded_bytes = base64.b64decode(base64_bytes)
        decoded_token = decoded_bytes.decode("ascii")
        return get_object_or_404(cls, token=decoded_token)
