from typing import Any

from graphene import (
    ID,
    Decimal,
    Field,
    InputObjectType,
    List,
    ObjectType,
)
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql_jwt.decorators import login_required

from accounts.filters import AccountFilter
from accounts.forms import (
    CreateAccountForm,
    DeleteAccountForm,
    OrderAccountForm,
    UpdateAccountForm,
)
from accounts.models import Account
from utils import filter_order_paginate
from utils.filter import filter_to_filter_input_class
from utils.order import form_to_order_argument
from utils.paginator import PaginatorQueryInput, PaginatorQueryPayload


class AccountType(DjangoObjectType):
    balance = Decimal()

    class Meta:
        model = Account
        fields = ("id", "currency", "name", "transaction_set")

    @staticmethod
    def resolve_balance(parent: Account, info):
        return parent.balance

    @staticmethod
    def resolve_transaction_set(parent: Account, info):
        return parent.transaction_set.order_by("datetime", "id")


# queries
class GetAccountQueryInput(InputObjectType):
    id = ID(required=True)


class GetAccountQueryPayload(ObjectType):
    data = Field(AccountType)


class ListAccountsQueryPayload(PaginatorQueryPayload, ObjectType):
    data = List(AccountType, required=True)


class AccountFilterQueryInput(filter_to_filter_input_class(AccountFilter)):  # type: ignore[misc]
    pass


class AccountQuery(ObjectType):
    get_account = Field(
        GetAccountQueryPayload, input=GetAccountQueryInput(required=True)
    )
    list_accounts = Field(
        ListAccountsQueryPayload,
        filter=AccountFilterQueryInput(),
        order=form_to_order_argument(OrderAccountForm),
        paginator=PaginatorQueryInput(),
    )

    @staticmethod
    @login_required
    def resolve_get_account(root, info, input: GetAccountQueryInput):
        data = Account._default_manager.get(
            pk=input.id, currency__user=info.context.user
        )
        return GetAccountQueryPayload(data=data)  # type: ignore

    @staticmethod
    @login_required
    def resolve_list_accounts(
        root,
        info,
        filter: AccountFilterQueryInput | None = None,
        order: list[Any] | None = None,
        paginator: PaginatorQueryInput | None = None,
    ):
        data = Account._default_manager.filter(currency__user=info.context.user)
        data, kwargs = filter_order_paginate(data, filter, order, paginator)
        return ListAccountsQueryPayload(data=data, **kwargs)  # type: ignore


# mutations
class CreateAccountMutation(DjangoModelFormMutation):
    class Meta:
        form_class = CreateAccountForm
        exclude_fields = ("id",)
        return_field_name = "data"

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        return super().mutate_and_get_payload(root, info, **input)


class ExistingAccountMutation(DjangoModelFormMutation):
    class Meta:
        abstract = True

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        return super().mutate_and_get_payload(root, info, **input)

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        kwargs = super().get_form_kwargs(root, info, **input)
        cls._meta.model._default_manager.filter(currency__user=info.context.user).get(
            pk=kwargs["instance"].pk  # type: ignore
        )
        return kwargs


class UpdateAccountMutation(ExistingAccountMutation):
    class Input:
        # manually define the required id for the input
        id = ID(required=True)

    class Meta:
        form_class = UpdateAccountForm
        # exclude the default provided non-required id field from the input
        exclude_fields = ("id",)
        return_field_name = "data"


class DeleteAccountMutation(ExistingAccountMutation):
    class Input:
        id = ID(required=True)

    class Meta:
        form_class = DeleteAccountForm
        exclude_fields = ("id",)
        return_field_name = "data"

    @classmethod
    def perform_mutate(cls, form: DeleteAccountForm, info):
        obj: Account = form.save(commit=False)
        instance: Account = form._meta.model._default_manager.get(pk=obj.pk)
        obj.delete()
        kwargs = {cls._meta.return_field_name: instance}
        return cls(errors=[], **kwargs)  # type: ignore


class AccountMutation(ObjectType):
    create_account = CreateAccountMutation.Field()
    update_account = UpdateAccountMutation.Field()
    delete_account = DeleteAccountMutation.Field()
