from django.contrib.auth.tokens import (
    PasswordResetTokenGenerator,
    default_token_generator,
)
from django.core.mail import send_mail
from graphene import Boolean, Field, Mutation, NonNull, ObjectType, String
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql_jwt import ObtainJSONWebToken, Verify
from graphql_jwt.decorators import ensure_token
from graphql_jwt.utils import get_payload, get_user_by_payload

from authentication.models import AuthReset
from users.forms import UpdateUserForm
from users.models import User
from users.schemas import CreateUserMutation, UserType


class AuthSignInMutationPayload(ObtainJSONWebToken):
    user = Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)


class AuthVerifyMutationPayload(Verify):
    user = Field(UserType)

    @classmethod
    @ensure_token
    def verify(cls, root, info, token, **kwargs):
        payload = get_payload(token, info.context)
        return cls(payload=payload, user=get_user_by_payload(payload))


class AuthSendResetMutationPayload(Mutation):
    class Arguments:
        # client url for password reset form with a {token} placeholder
        # e.g. xyz.com/{token}
        url = String(required=True)
        email = String(required=True)

    token_generator: PasswordResetTokenGenerator = default_token_generator

    sent = NonNull(Boolean)

    @classmethod
    def generate_url(cls, url: str, reset: AuthReset):
        return str(url.format(token=reset.encode()))

    @classmethod
    def create(cls, user: User) -> AuthReset:
        reset = AuthReset._default_manager.filter(user=user).first()
        token = cls.token_generator.make_token(user)
        if reset:
            reset.delete()
        return AuthReset._default_manager.create(user=user, token=token)

    @classmethod
    def send(cls, url: str, email: str):
        return bool(
            send_mail(
                "ThriftEase: Password Reset Link",
                f"{url}",
                "mail@thriftease.com.ph",
                [email],
                fail_silently=False,
            )
        )

    @classmethod
    def mutate(cls, root, info, url: str, email: str):
        try:
            user = User.objects.get(email=email)
            reset = cls.create(user)
            redirect_url = cls.generate_url(url, reset)
            return cls(sent=cls.send(redirect_url, user.email))
        except Exception:
            return cls(sent=False)


class AuthApplyResetMutation(DjangoModelFormMutation):
    class Input:
        token = String(required=True)
        password = String(required=True)

    class Meta:
        form_class = UpdateUserForm
        exclude_fields = (
            "id",
            "email",
            "password",
            "given_name",
            "middle_name",
            "family_name",
            "suffix",
        )
        return_field_name = "data"

    @classmethod
    def mutate_and_get_payload(cls, root, info, token: str, **input):
        reset = AuthReset.decode(token)
        input["id"] = reset.user.pk
        rv = super().mutate_and_get_payload(root, info, **input)
        if not rv.errors:
            reset.delete()
        return rv


class AuthQuery(ObjectType):
    auth_existing = Field(Boolean, email=NonNull(String))

    @staticmethod
    def resolve_auth_existing(root, info, email: str):
        try:
            User.objects.get(email=email)
            return True
        except Exception:
            return False


class AuthMutation(ObjectType):
    auth_sign_in = AuthSignInMutationPayload.Field()
    auth_sign_up = CreateUserMutation.Field()
    auth_verify = AuthVerifyMutationPayload.Field()
    auth_send_reset = AuthSendResetMutationPayload.Field()
    auth_apply_reset = AuthApplyResetMutation.Field()
