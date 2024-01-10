from graphene import Boolean, Field, NonNull, ObjectType, String
from graphql_jwt import ObtainJSONWebToken, Verify
from graphql_jwt.decorators import ensure_token
from graphql_jwt.utils import get_payload, get_user_by_payload

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
