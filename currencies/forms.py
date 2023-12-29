from django import forms

from currencies.models import Currency
from utils import formfield_extra_kwargs


class CreateCurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = (
            "user",
            "abbreviation",
            "symbol",
            "name",
        )


class UpdateCurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = (
            "symbol",
            "name",
        )
        formfield_callback = formfield_extra_kwargs(
            symbol=dict(required=False),
            name=dict(required=False),
        )


class DeleteCurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ()


class OrderCurrencyForm(forms.ModelForm):
    id = forms.IntegerField()

    class Meta:
        model = Currency
        fields = (
            "id",
            "user",
            "abbreviation",
            "symbol",
            "name",
        )
