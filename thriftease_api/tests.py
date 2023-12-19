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
    def CreateUserMutationInput(cls, *args):
        return (
            """
        {
            email: "%s"
            password: "%s"
            givenName: "%s"
            middleName: "%s"
            familyName: "%s"
            suffix: "%s"
        }
        """
            % args
        )

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
    def createUser(cls, *args):
        return f"""
        createUser(input: {cls.CreateUserMutationInput(*args)}) {{
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
