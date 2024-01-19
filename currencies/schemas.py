from typing import Any

import requests as req
from forex_python.converter import CurrencyCodes
from graphene import (
    ID,
    Field,
    InputObjectType,
    List,
    NonNull,
    ObjectType,
    String,
)
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql_jwt.decorators import login_required

from currencies.filters import CurrencyFilter
from currencies.forms import (
    CreateCurrencyForm,
    DeleteCurrencyForm,
    OrderCurrencyForm,
    UpdateCurrencyForm,
)
from currencies.models import Currency
from utils import filter_order_paginate
from utils.filter import filter_to_filter_input_class
from utils.order import form_to_order_argument
from utils.paginator import PaginatorQueryInput, PaginatorQueryPayload


class GivenCurrencyType(DjangoObjectType):
    class Meta:
        model = Currency
        fields = (
            "abbreviation",
            "symbol",
            "name",
        )


class CurrencyType(DjangoObjectType):
    class Meta:
        model = Currency
        fields = (
            "id",
            "user",
            "abbreviation",
            "symbol",
            "name",
        )


# queries
class GetCurrencyQueryInput(InputObjectType):
    id = ID(required=True)


class GetCurrencyQueryPayload(ObjectType):
    data = Field(CurrencyType)


class ListCurrenciesQueryPayload(PaginatorQueryPayload, ObjectType):
    data = List(CurrencyType, required=True)


class CurrencyFilterQueryInput(filter_to_filter_input_class(CurrencyFilter)):  # type: ignore[misc]
    abbreviation__in = List(NonNull(String))


class CurrencyQuery(ObjectType):
    get_currency = Field(
        GetCurrencyQueryPayload, input=GetCurrencyQueryInput(required=True)
    )
    list_currencies = Field(
        ListCurrenciesQueryPayload,
        filter=CurrencyFilterQueryInput(),
        order=form_to_order_argument(OrderCurrencyForm),
        paginator=PaginatorQueryInput(),
    )
    list_given_currencies = List(NonNull(GivenCurrencyType))

    @staticmethod
    @login_required
    def resolve_get_currency(root, info, input: GetCurrencyQueryInput):
        data = Currency._default_manager.get(pk=input.id, user=info.context.user)
        return GetCurrencyQueryPayload(data=data)  # type: ignore

    @staticmethod
    @login_required
    def resolve_list_given_currencies(root, info):
        res = req.get(
            "https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies.min.json"
        )
        rv = []
        if res.status_code == 200:
            result: dict[str, str] = res.json()  # type: ignore
            if result:
                codes = CurrencyCodes()
                for key, val in result.items():
                    ukey = key.upper()
                    print(ukey, codes.get_symbol(ukey))
                    symbol = codes.get_symbol(ukey) or ukey
                    rv.append(
                        GivenCurrencyType(
                            abbreviation=key, name=val or key, symbol=symbol
                        )  # type: ignore
                    )

        return rv

    @staticmethod
    @login_required
    def resolve_list_currencies(
        root,
        info,
        filter: CurrencyFilterQueryInput | None = None,
        order: list[Any] | None = None,
        paginator: PaginatorQueryInput | None = None,
    ):
        data = Currency._default_manager.filter(user=info.context.user)
        data, kwargs = filter_order_paginate(data, filter, order, paginator)
        return ListCurrenciesQueryPayload(data=data, **kwargs)  # type: ignore


# mutations
class CreateCurrencyMutation(DjangoModelFormMutation):
    class Meta:
        form_class = CreateCurrencyForm
        exclude_fields = ("id", "user")
        return_field_name = "data"

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        input["user"] = info.context.user.id
        return super().mutate_and_get_payload(root, info, **input)


class ExistingCurrencyMutation(DjangoModelFormMutation):
    class Meta:
        abstract = True

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        return super().mutate_and_get_payload(root, info, **input)

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        kwargs = super().get_form_kwargs(root, info, **input)
        cls._meta.model._default_manager.filter(user=info.context.user).get(
            pk=kwargs["instance"].pk  # type: ignore
        )
        return kwargs


class UpdateCurrencyMutation(ExistingCurrencyMutation):
    class Input:
        # manually define the required id for the input
        id = ID(required=True)

    class Meta:
        form_class = UpdateCurrencyForm
        # exclude the default provided non-required id field from the input
        exclude_fields = ("id",)
        return_field_name = "data"


class DeleteCurrencyMutation(ExistingCurrencyMutation):
    class Input:
        id = ID(required=True)

    class Meta:
        form_class = DeleteCurrencyForm
        exclude_fields = ("id",)
        return_field_name = "data"

    @classmethod
    def perform_mutate(cls, form: DeleteCurrencyForm, info):
        obj: Currency = form.save(commit=False)
        instance: Currency = form._meta.model._default_manager.get(pk=obj.pk)
        obj.delete()
        kwargs = {cls._meta.return_field_name: instance}
        return cls(errors=[], **kwargs)  # type: ignore


class CurrencyMutation(ObjectType):
    create_currency = CreateCurrencyMutation.Field()
    update_currency = UpdateCurrencyMutation.Field()
    delete_currency = DeleteCurrencyMutation.Field()
