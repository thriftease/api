from graphene import ObjectType
from graphql_jwt import ObtainJSONWebToken, Verify

from users.schemas import CreateUserMutation


class AuthMutation(ObjectType):
    auth_sign_in = ObtainJSONWebToken.Field()
    auth_sign_up = CreateUserMutation.Field()
    auth_verify = Verify.Field()
