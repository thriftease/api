from django import forms

from users.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "given_name",
            "middle_name",
            "family_name",
            "suffix",
        )
