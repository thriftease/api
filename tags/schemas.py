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

from tags.filters import TagFilter
from tags.forms import (
    CreateTagForm,
    DeleteTagForm,
    OrderTagForm,
    UpdateTagForm,
)
from tags.models import Tag
from utils import filter_order_paginate
from utils.filter import filter_to_filter_input_class
from utils.order import form_to_order_argument
from utils.paginator import PaginatorQueryInput, PaginatorQueryPayload


class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = (
            "id",
            "user",
            "name",
        )


# queries
class GetTagQueryInput(InputObjectType):
    id = ID(required=True)


class GetTagQueryPayload(ObjectType):
    data = Field(TagType)


class ListTagsQueryPayload(PaginatorQueryPayload, ObjectType):
    data = List(TagType, required=True)


class TagFilterQueryInput(filter_to_filter_input_class(TagFilter)):  # type: ignore[misc]
    pass


class TagQuery(ObjectType):
    get_tag = Field(GetTagQueryPayload, input=GetTagQueryInput(required=True))
    list_tags = Field(
        ListTagsQueryPayload,
        filter=TagFilterQueryInput(),
        order=form_to_order_argument(OrderTagForm),
        paginator=PaginatorQueryInput(),
    )

    @staticmethod
    @login_required
    def resolve_get_tag(root, info, input: GetTagQueryInput):
        data = Tag._default_manager.get(pk=input.id, user=info.context.user)
        return GetTagQueryPayload(data=data)  # type: ignore

    @staticmethod
    @login_required
    def resolve_list_tags(
        root,
        info,
        filter: TagFilterQueryInput | None = None,
        order: list[Any] | None = None,
        paginator: PaginatorQueryInput | None = None,
    ):
        data = Tag._default_manager.filter(user=info.context.user)
        data, kwargs = filter_order_paginate(data, filter, order, paginator)
        return ListTagsQueryPayload(data=data, **kwargs)  # type: ignore


# mutations
class CreateTagMutation(DjangoModelFormMutation):
    class Meta:
        form_class = CreateTagForm
        exclude_fields = ("id", "user")
        return_field_name = "data"

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        input["user"] = info.context.user.id
        return super().mutate_and_get_payload(root, info, **input)


class ExistingTagMutation(DjangoModelFormMutation):
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


class UpdateTagMutation(ExistingTagMutation):
    class Input:
        # manually define the required id for the input
        id = ID(required=True)

    class Meta:
        form_class = UpdateTagForm
        # exclude the default provided non-required id field from the input
        exclude_fields = ("id",)
        return_field_name = "data"


class DeleteTagMutation(ExistingTagMutation):
    class Input:
        id = ID(required=True)

    class Meta:
        form_class = DeleteTagForm
        exclude_fields = ("id",)
        return_field_name = "data"

    @classmethod
    def perform_mutate(cls, form: DeleteTagForm, info):
        obj: Tag = form.save(commit=False)
        instance: Tag = form._meta.model._default_manager.get(pk=obj.pk)
        obj.delete()
        kwargs = {cls._meta.return_field_name: instance}
        return cls(errors=[], **kwargs)  # type: ignore


class TagMutation(ObjectType):
    create_tag = CreateTagMutation.Field()
    update_tag = UpdateTagMutation.Field()
    delete_tag = DeleteTagMutation.Field()
