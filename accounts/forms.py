from django import forms

from accounts.models import Account
from utils import formfield_extra_kwargs


class CreateAccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = (
            "currency",
            "name",
        )


class UpdateAccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = (
            "currency",
            "name",
        )
        formfield_callback = formfield_extra_kwargs(
            currency=dict(required=False),
            name=dict(required=False),
        )


class DeleteAccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ()


class OrderAccountForm(forms.ModelForm):
    id = forms.IntegerField()
    balance = forms.DecimalField()
    future_balance = forms.DecimalField()

    class Meta:
        model = Account
        fields = ("id", "currency", "name")
