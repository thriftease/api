from typing import Any

from thriftease_api.gql import Schema
from utils.gql import GqlAction, GqlArgument, GqlType


class UserSchema(Schema):
    ErrorType = GqlType("field", "messages")
    UserType = GqlType(
        "id", "email", "given_name", "middle_name", "family_name", "suffix", "full_name"
    )
    UserPayload = GqlType(data=UserType, errors=ErrorType)
    CreateUserMutationInput = GqlArgument(
        input=GqlArgument(
            email=None,
            password=None,
            given_name=None,
            middle_name=None,
            family_name=None,
            suffix=None,
        )
    )
    UpdateUserMutationInput = GqlArgument(
        input=GqlArgument(
            id=None,
            password=None,
            given_name=None,
            middle_name=None,
            family_name=None,
            suffix=None,
        )
    )
    DeleteUserMutationInput = GqlArgument(
        input=GqlArgument(
            id=None,
        )
    )

    @classmethod
    def createUser(cls, **kwargs):
        act = GqlAction(
            "createUser",
            cls.CreateUserMutationInput(input=kwargs),
            cls.UserPayload,
        )
        return act

    @classmethod
    def updateUser(cls, **kwargs):
        act = GqlAction(
            "updateUser",
            cls.UpdateUserMutationInput(input=kwargs),
            cls.UserPayload,
        )
        return act

    @classmethod
    def deleteUser(cls, id: Any):
        act = GqlAction(
            "deleteUser",
            cls.DeleteUserMutationInput(input=dict(id=id)),
            cls.UserPayload,
        )
        return act
