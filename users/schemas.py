from graphene import ID, Field, InputObjectType, List, ObjectType, String
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

from users.forms import CreateUserForm, DeleteUserForm, UpdateUserForm
from users.models import User
from utils import PaginatorQueryInput, PaginatorQueryPayload


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
        # filterset_class = UserFilter
        # interfaces = (relay.Node,)

    @staticmethod
    def resolve_full_name(parent: User, info):
        return parent.full_name


# queries
class GetUserQueryInput(InputObjectType):
    id = ID(required=True)


class GetUserQueryPayload(ObjectType):
    data = Field(UserType)


class ListUsersQueryInput(InputObjectType):
    pass


class ListUsersQueryPayload(PaginatorQueryPayload, ObjectType):
    data = List(UserType, required=True)


class UserQuery(ObjectType):
    # get_user = relay.Node.Field(UserType)
    # list_users = DjangoFilterConnectionField(UserType)
    get_user = Field(GetUserQueryPayload, input=GetUserQueryInput(required=True))
    list_users = Field(ListUsersQueryPayload, paginator=PaginatorQueryInput())

    @staticmethod
    def resolve_get_user(root, info, input: GetUserQueryInput):
        return GetUserQueryPayload(data=User.objects.get(pk=input.id))  # type: ignore

    @staticmethod
    def resolve_list_users(
        root,
        info,
        paginator: PaginatorQueryInput | None = None,
    ):
        data = User.objects.all().order_by("id")
        paginator = paginator or PaginatorQueryInput()
        data, dpaginator = paginator.paginate(data)
        return ListUsersQueryPayload(data=data, paginator=dpaginator)  # type: ignore


# mutations
class CreateUserMutation(DjangoModelFormMutation):
    class Meta:
        form_class = CreateUserForm
        exclude_fields = ("id",)
        return_field_name = "data"


class UpdateUserMutation(DjangoModelFormMutation):
    class Input:
        # manually define the required id for the input
        id = ID(required=True)

    class Meta:
        form_class = UpdateUserForm
        # exclude the default provided non-required id field from the input
        exclude_fields = ("id",)
        return_field_name = "data"


class DeleteUserMutation(DjangoModelFormMutation):
    class Input:
        id = ID(required=True)

    class Meta:
        form_class = DeleteUserForm
        exclude_fields = ("id",)
        return_field_name = "data"

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
