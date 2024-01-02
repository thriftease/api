from django import forms

from transactions.models import Transaction
from utils import formfield_extra_kwargs


class CreateTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = (
            "account",
            "amount",
            "datetime",
            "name",
            "description",
        )
        formfield_callback = formfield_extra_kwargs(
            amount=dict(required=False),
            datetime=dict(required=False),
            name=dict(required=False),
            description=dict(required=False),
        )


class UpdateTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = (
            "account",
            "amount",
            "datetime",
            "name",
            "description",
        )
        formfield_callback = formfield_extra_kwargs(
            account=dict(required=False),
            amount=dict(required=False),
            datetime=dict(required=False),
            name=dict(required=False),
            description=dict(required=False),
        )


class DeleteTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ()


class OrderTransactionForm(forms.ModelForm):
    id = forms.IntegerField()

    class Meta:
        model = Transaction
        fields = (
            "id",
            "datetime",
        )
