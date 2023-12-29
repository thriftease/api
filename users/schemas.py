from graphene import (
    Field,
    ObjectType,
    String,
)
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql_jwt.decorators import login_required

from users.forms import CreateUserForm, DeleteUserForm, UpdateUserForm
from users.models import User


class UserType(DjangoObjectType):
    full_name = String()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "given_name",
            "middle_name",
            "family_name",
            "suffix",
        )

    @staticmethod
    def resolve_full_name(parent: User, info):
        return parent.full_name


# queries
class GetUserQueryPayload(ObjectType):
    data = Field(UserType)


class UserQuery(ObjectType):
    get_user = Field(GetUserQueryPayload)

    @staticmethod
    @login_required
    def resolve_get_user(root, info):
        data = info.context.user
        return GetUserQueryPayload(data=data)  # type: ignore


# mutations
class CreateUserMutation(DjangoModelFormMutation):
    class Meta:
        form_class = CreateUserForm
        exclude_fields = ("id",)
        return_field_name = "data"


class UpdateUserMutation(DjangoModelFormMutation):
    class Meta:
        form_class = UpdateUserForm
        # exclude the default provided non-required id field from the input
        exclude_fields = ("id",)
        return_field_name = "data"

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        input["id"] = info.context.user.id
        return super().mutate_and_get_payload(root, info, **input)


class DeleteUserMutation(DjangoModelFormMutation):
    class Meta:
        form_class = DeleteUserForm
        exclude_fields = ("id",)
        return_field_name = "data"

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        input["id"] = info.context.user.id
        return super().mutate_and_get_payload(root, info, **input)

    @classmethod
    def perform_mutate(cls, form: DeleteUserForm, info):
        obj: User = form.save(commit=False)
        instance: User = form._meta.model._default_manager.get(pk=obj.pk)
        obj.delete()
        kwargs = {cls._meta.return_field_name: instance}
        return cls(errors=[], **kwargs)  # type: ignore


class UserMutation(ObjectType):
    create_user = CreateUserMutation.Field()
    update_user = UpdateUserMutation.Field()
    delete_user = DeleteUserMutation.Field()
