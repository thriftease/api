from typing import Any

import pytest
from graphene_django.utils.testing import graphql_query


@pytest.mark.django_db
class TestGraphQL:
    @pytest.fixture
    @staticmethod
    def gql(client):
        def func(*args, **kwargs):
            return graphql_query(*args, **kwargs, client=client)

        return func

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
