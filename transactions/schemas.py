from typing import Any

from graphene import (
    ID,
    Decimal,
    Field,
    InputObjectType,
    List,
    NonNull,
    ObjectType,
    String,
)
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import (
    DjangoModelFormMutation,
    _set_errors_flag_to_context,
)
from graphene_django.types import ErrorType
from graphql_jwt.decorators import login_required

from tags.models import Tag
from transactions.filters import TransactionFilter
from transactions.forms import (
    CreateTransactionForm,
    DeleteTransactionForm,
    OrderTransactionForm,
    UpdateTransactionForm,
)
from transactions.models import Transaction
from utils import filter_order_paginate
from utils.filter import filter_to_filter_input_class
from utils.order import form_to_order_argument
from utils.paginator import PaginatorQueryInput, PaginatorQueryPayload


class TransactionType(DjangoObjectType):
    resulting_account_balance = Decimal()

    class Meta:
        model = Transaction
        fields = (
            "id",
            "account",
            "amount",
            "datetime",
            "name",
            "description",
            "tag_set",
        )

    @staticmethod
    def resolve_resulting_account_balance(parent: Transaction, info):
        return parent.resulting_account_balance


# queries
class GetTransactionQueryInput(InputObjectType):
    id = ID(required=True)


class GetTransactionQueryPayload(ObjectType):
    data = Field(TransactionType)


class ListTransactionsQueryPayload(PaginatorQueryPayload, ObjectType):
    data = List(TransactionType, required=True)


class TransactionFilterQueryInput(filter_to_filter_input_class(TransactionFilter)):  # type: ignore[misc]
    pass


class TransactionQuery(ObjectType):
    get_transaction = Field(
        GetTransactionQueryPayload, input=GetTransactionQueryInput(required=True)
    )
    list_transactions = Field(
        ListTransactionsQueryPayload,
        filter=TransactionFilterQueryInput(),
        order=form_to_order_argument(OrderTransactionForm),
        paginator=PaginatorQueryInput(),
    )

    @staticmethod
    @login_required
    def resolve_get_transaction(root, info, input: GetTransactionQueryInput):
        data = Transaction._default_manager.get(
            pk=input.id, account__currency__user=info.context.user
        )
        return GetTransactionQueryPayload(data=data)  # type: ignore

    @staticmethod
    @login_required
    def resolve_list_transactions(
        root,
        info,
        filter: TransactionFilterQueryInput | None = None,
        order: list[Any] | None = None,
        paginator: PaginatorQueryInput | None = None,
    ):
        data = Transaction._default_manager.filter(
            account__currency__user=info.context.user
        )
        data, kwargs = filter_order_paginate(data, filter, order, paginator)
        return ListTransactionsQueryPayload(data=data, **kwargs)  # type: ignore


def tag(transaction: Transaction, tags: list[str], tag_ids: list[str]):
    existing_tags = []
    new_tags = []
    for t in tags:
        tg = Tag._default_manager.filter(
            user=transaction.account.currency.user, name=t
        ).first()
        if tg:
            existing_tags.append(tg)
        else:
            new_tags.append(Tag(user=transaction.account.currency.user, name=t))
    for t in tag_ids:
        tg = Tag._default_manager.filter(
            user=transaction.account.currency.user, pk=t
        ).first()
        if tg:
            existing_tags.append(tg)
    Tag._default_manager.bulk_create(new_tags, ignore_conflicts=True)
    transaction.tag_set.add(*existing_tags, *new_tags)  # type: ignore


def untag(transaction: Transaction, tags: list[str], tag_ids: list[str]):
    existing_tags = []
    for t in tags:
        tg = Tag._default_manager.filter(
            user=transaction.account.currency.user, name=t
        ).first()
        if tg:
            existing_tags.append(tg)
    for t in tag_ids:
        tg = Tag._default_manager.filter(
            user=transaction.account.currency.user, pk=t
        ).first()
        if tg:
            existing_tags.append(tg)
    transaction.tag_set.remove(*existing_tags)  # type: ignore


# mutations
class CreateTransactionMutation(DjangoModelFormMutation):
    class Input:
        tags = List(NonNull(String))
        tag_ids = List(NonNull(ID))

    class Meta:
        form_class = CreateTransactionForm
        exclude_fields = ("id",)
        return_field_name = "data"

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        tags = input.pop("tags", [])
        tag_ids = input.pop("tag_ids", [])
        form = cls.get_form(root, info, **input)

        if form.is_valid():
            rv = cls.perform_mutate(form, info)
            tag(form.instance, tags, tag_ids)
            return rv
        else:
            errors = ErrorType.from_errors(form.errors)
            _set_errors_flag_to_context(info)

            return cls(errors=errors)


class ExistingTransactionMutation(DjangoModelFormMutation):
    class Meta:
        abstract = True

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        return super().mutate_and_get_payload(root, info, **input)

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        kwargs = super().get_form_kwargs(root, info, **input)
        cls._meta.model._default_manager.filter(
            account__currency__user=info.context.user
        ).get(
            pk=kwargs["instance"].pk  # type: ignore
        )
        return kwargs


class UpdateTransactionMutation(ExistingTransactionMutation):
    class Input:
        # manually define the required id for the input
        id = ID(required=True)
        add_tags = List(NonNull(String))
        add_tag_ids = List(NonNull(ID))
        remove_tags = List(NonNull(String))
        remove_tag_ids = List(NonNull(ID))

    class Meta:
        form_class = UpdateTransactionForm
        # exclude the default provided non-required id field from the input
        exclude_fields = ("id",)
        return_field_name = "data"

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        add_tags = input.pop("add_tags", [])
        add_tag_ids = input.pop("add_tag_ids", [])
        remove_tags = input.pop("remove_tags", [])
        remove_tag_ids = input.pop("remove_tag_ids", [])
        form = cls.get_form(root, info, **input)

        if form.is_valid():
            rv = cls.perform_mutate(form, info)
            untag(form.instance, remove_tags, remove_tag_ids)
            tag(form.instance, add_tags, add_tag_ids)
            return rv
        else:
            errors = ErrorType.from_errors(form.errors)
            _set_errors_flag_to_context(info)

            return cls(errors=errors)


class DeleteTransactionMutation(ExistingTransactionMutation):
    class Input:
        id = ID(required=True)

    class Meta:
        form_class = DeleteTransactionForm
        exclude_fields = ("id",)
        return_field_name = "data"

    @classmethod
    def perform_mutate(cls, form: DeleteTransactionForm, info):
        obj: Transaction = form.save(commit=False)
        instance: Transaction = form._meta.model._default_manager.get(pk=obj.pk)
        obj.delete()
        kwargs = {cls._meta.return_field_name: instance}
        return cls(errors=[], **kwargs)  # type: ignore


class TransactionMutation(ObjectType):
    create_transaction = CreateTransactionMutation.Field()
    update_transaction = UpdateTransactionMutation.Field()
    delete_transaction = DeleteTransactionMutation.Field()
