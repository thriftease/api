from typing import Any

from graphene import (
    ID,
    Field,
    InputObjectType,
    List,
    ObjectType,
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
from utils import filter_order_paginate, info_user_check
from utils.filter import filter_to_filter_input_class
from utils.order import form_to_order_argument
from utils.paginator import PaginatorQueryInput, PaginatorQueryPayload


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


class ListCurrenciesQueryInput(InputObjectType):
    pass


class ListCurrenciesQueryPayload(PaginatorQueryPayload, ObjectType):
    data = List(CurrencyType, required=True)


class CurrencyFilterQueryInput(filter_to_filter_input_class(CurrencyFilter)):  # type: ignore[misc]
    pass


class CurrencyQuery(ObjectType):
    get_currency = Field(
        GetCurrencyQueryPayload, input=GetCurrencyQueryInput(required=True)
    )
    list_currency = Field(
        ListCurrenciesQueryPayload,
        filter=CurrencyFilterQueryInput(),
        order=form_to_order_argument(OrderCurrencyForm),
        paginator=PaginatorQueryInput(),
    )

    @staticmethod
    @login_required
    def resolve_get_currencie(root, info, input: GetCurrencyQueryInput):
        data = Currency._default_manager.get(pk=input.id)
        info_user_check(info, data.user)
        return GetCurrencyQueryPayload(data=data)  # type: ignore

    @staticmethod
    @login_required
    def resolve_list_currencies(
        root,
        info,
        filter: CurrencyFilterQueryInput | None = None,
        order: list[Any] | None = None,
        paginator: PaginatorQueryInput | None = None,
    ):
        data = Currency._default_manager.filter(pk=info.context.currencie.pk)
        data, kwargs = filter_order_paginate(data, filter, order, paginator)
        return ListCurrenciesQueryPayload(data=data, **kwargs)  # type: ignore


# mutations
class CreateCurrencyMutation(DjangoModelFormMutation):
    class Meta:
        form_class = CreateCurrencyForm
        exclude_fields = ("id", "user")
        return_field_name = "data"

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        input["user"] = info.context.user.id
        return super().mutate_and_get_payload(root, info, **input)


class UpdateCurrencyMutation(DjangoModelFormMutation):
    class Input:
        # manually define the required id for the input
        id = ID(required=True)

    class Meta:
        form_class = UpdateCurrencyForm
        # exclude the default provided non-required id field from the input
        exclude_fields = ("id",)
        return_field_name = "data"

    @classmethod
    @login_required
    def perform_mutate(cls, form, info):
        info_user_check(info, form.instance.user)
        return super().perform_mutate(form, info)


class DeleteCurrencyMutation(DjangoModelFormMutation):
    class Input:
        id = ID(required=True)

    class Meta:
        form_class = DeleteCurrencyForm
        exclude_fields = ("id",)
        return_field_name = "data"

    @classmethod
    @login_required
    def perform_mutate(cls, form: DeleteCurrencyForm, info):
        info_user_check(info, form.instance)
        obj: Currency = form.save(commit=False)
        instance: Currency = form._meta.model._default_manager.get(pk=obj.pk)
        obj.delete()
        kwargs = {cls._meta.return_field_name: instance}
        return cls(errors=[], **kwargs)  # type: ignore


class CurrencyMutation(ObjectType):
    create_currency = CreateCurrencyMutation.Field()
    update_currency = UpdateCurrencyMutation.Field()
    delete_currency = DeleteCurrencyMutation.Field()
