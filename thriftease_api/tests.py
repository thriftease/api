import json
from typing import Any

import pytest
from graphene_django.utils.testing import graphql_query


@pytest.mark.django_db
class Schema:
    @pytest.fixture
    @staticmethod
    def gql(client):
        def func(*args, **kwargs):
            return graphql_query(*args, **kwargs, client=client)

        return func

    @classmethod
    def to_value(cls, value: Any):
        if isinstance(value, str):
            return f'"{value}"'
        elif value is None:
            return "null"
        return str(value)

    @classmethod
    def to_key_value(cls, key: str, value: Any):
        key = "".join(
            map(
                lambda e: (e[1][0].lower() if e[0] == 0 else e[1][0].upper())
                + e[1][1:],
                enumerate(key.split("_")),
            )
        )
        return f"{key}: {cls.to_value(value)}"

    @classmethod
    def to_object(cls, **kwargs):
        return f"""
            {{
                {"\n".join(cls.to_key_value(k, v) for k, v in kwargs.items())}
            }}
        """

    @classmethod
    def CreateUserMutationInput(cls, **kwargs):
        kw = dict(
            email="",
            password="",
            given_name="",
            middle_name=None,
            family_name="",
            suffix=None,
        )
        kw.update(kwargs)
        return cls.to_object(**kw)

    @classmethod
    def UpdateUserMutationInput(cls, **kwargs):
        kw = dict(
            id=0,
            password=None,
            given_name=None,
            middle_name=None,
            family_name=None,
            suffix=None,
        )
        kw.update(kwargs)
        return cls.to_object(**kw)

    @classmethod
    def DeleteUserMutationInput(cls, id):
        kw = dict(id=id)
        return cls.to_object(**kw)

    @classmethod
    def GetUserQueryInput(cls, id):
        kw = dict(id=id)
        return cls.to_object(**kw)

    @classmethod
    def FilterOrderPaginatorQueryInput(cls, filter={}, order={}, paginator={}):
        args = []
        for d in (filter, order, paginator):
            args.append(cls.to_object(**d) if d else cls.to_value(None))
        return cls.to_object(**dict(filter=filter, order=order, paginator=paginator))

    @classmethod
    def ListUsersQueryInput(cls, filter={}, order={}, paginator={}):
        return cls.FilterOrderPaginatorQueryInput(filter, order, paginator)

    @classmethod
    def UserType(cls):
        return """
        {
            email
            givenName
            middleName
            familyName
            suffix
            fullName
        }
        """

    @classmethod
    def ErrorType(cls):
        return """
        {
            field, messages
        }
        """

    @classmethod
    def authSignIn(cls, **kwargs):
        return f"""
        authSignIn(email: {cls.to_value(kwargs['email'])}, password: {cls.to_value(kwargs['password'])}) {{
            payload
            refreshExpiresIn
            user {cls.UserType()}
            token
        }}
        """

    @classmethod
    def authVerify(cls, token: str):
        return f"""
        authVerify(token: {cls.to_value(token)}) {{
            payload
            user {cls.UserType()}
        }}
        """

    @classmethod
    def authSignUp(cls, **kwargs):
        return f"""
        authSignUp(input: {cls.CreateUserMutationInput(**kwargs)}) {{
            data {cls.UserType()}
            errors {cls.ErrorType()}
        }}
        """

    @classmethod
    def createUser(cls, **kwargs):
        return f"""
        createUser(input: {cls.CreateUserMutationInput(**kwargs)}) {{
            data {cls.UserType()}
            errors {cls.ErrorType()}
        }}
        """

    @classmethod
    def updateUser(cls, **kwargs):
        return f"""
        updateUser(input: {cls.UpdateUserMutationInput(**kwargs)}) {{
            data {cls.UserType()}
            errors {cls.ErrorType()}
        }}
        """

    @classmethod
    def deleteUser(cls, id):
        return f"""
        deleteUser(input: {cls.DeleteUserMutationInput(id)}) {{
            data {cls.UserType()}
            errors {cls.ErrorType()}
        }}
        """

    @classmethod
    def getUser(cls, id):
        return f"""
        getUser(input: {cls.GetUserQueryInput(id)}) {{
            data {cls.UserType()}
            errors {cls.ErrorType()}
        }}
        """

    @classmethod
    def mutation(cls, *mutations: str):
        return f"""
        mutation {{
            {"\n".join(mutations)}
        }}
        """

    @classmethod
    def query(cls, *queries: str):
        return f"""
        query {{
            {"\n".join(queries)}
        }}
        """

    @classmethod
    def has_field_error(
        cls, content: dict[str, Any], operation: str, field: str, *messages: str
    ):
        errors: list[dict[str, Any]] = content["data"][operation]["errors"]
        for e in errors:
            if e["field"] == field:
                if not messages:
                    return True
                else:
                    for m in messages:
                        if m in e["messages"]:
                            return True
        return False

    @classmethod
    def has_error(cls, content: dict[str, Any], operation: str, *messages: str):
        errors: list[dict[str, Any]] = content["errors"]
        for e in errors:
            if operation in e["path"]:
                if not messages:
                    return True
                else:
                    for m in messages:
                        if m == e["message"]:
                            return True
        return False

    def sign_in(self, gql: Any, **kwargs):
        response = gql(self.mutation(self.authSignIn(**kwargs)))
        content = json.loads(response.content)
        return dict(HTTP_AUTHORIZATION=f'JWT {content["data"]["authSignIn"]["token"]}')
