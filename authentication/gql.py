from thriftease_api.gql import Schema
from users.gql import UserSchema
from utils.gql import GqlAction, GqlArgument, GqlType


class AuthSchema(Schema):
    AuthSignInMutationInput = GqlArgument(email=None, password=None)
    AuthSignInMutationPayload = GqlType(
        "payload", "refreshExpiresIn", "token", user=UserSchema.UserType
    )
    AuthSignUpMutationInput = UserSchema.CreateUserMutationInput
    AuthSignUpMutationPayload = UserSchema.UserPayload
    AuthVerifyMutationInput = GqlArgument(token=None)
    AuthVerifyMutationPayload = GqlType("payload", user=UserSchema.UserType)

    @classmethod
    def authSignIn(cls, email: str, password: str):
        act = GqlAction(
            "authSignIn",
            cls.AuthSignInMutationInput(email=email, password=password),
            cls.AuthSignInMutationPayload,
        )
        return act

    @classmethod
    def authVerify(cls, token: str):
        act = GqlAction(
            "authVerify",
            cls.AuthVerifyMutationInput(token=token),
            cls.AuthVerifyMutationPayload,
        )
        return act

    @classmethod
    def authSignUp(cls, **kwargs):
        act = GqlAction(
            "authSignUp",
            cls.AuthSignUpMutationInput(input=kwargs),
            cls.AuthSignUpMutationPayload,
        )
        return act
