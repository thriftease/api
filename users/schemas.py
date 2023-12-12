from graphene import Field, ObjectType, String
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

from users.forms import UserForm
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


class CreateUserMutation(DjangoModelFormMutation):
    user = Field(UserType)

    class Meta:
        form_class = UserForm


class UserQuery(ObjectType):
    pass


class UserMutation(ObjectType):
    create_user = CreateUserMutation.Field()
