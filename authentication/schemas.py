from graphene import Field, ObjectType
from graphql_jwt import ObtainJSONWebToken, Verify
from graphql_jwt.decorators import ensure_token
from graphql_jwt.utils import get_payload, get_user_by_payload

from users.schemas import CreateUserMutation, UserType


class AuthSignInMutation(ObtainJSONWebToken):
    user = Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)


class AuthVerifyMutation(Verify):
    user = Field(UserType)

    @classmethod
    @ensure_token
    def verify(cls, root, info, token, **kwargs):
        payload = get_payload(token, info.context)
        return cls(payload=payload, user=get_user_by_payload(payload))


class AuthMutation(ObjectType):
    auth_sign_in = AuthSignInMutation.Field()
    auth_sign_up = CreateUserMutation.Field()
    auth_verify = AuthVerifyMutation.Field()
