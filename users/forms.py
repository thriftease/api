from django import forms

from users.models import User
from utils import formfield_extra_kwargs


class CreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "given_name",
            "middle_name",
            "family_name",
            "suffix",
        )


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "password",
            "given_name",
            "middle_name",
            "family_name",
            "suffix",
        )
        formfield_callback = formfield_extra_kwargs(
            password=dict(required=False),
            given_name=dict(required=False),
            family_name=dict(required=False),
        )


class DeleteUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ()
