import json
from typing import Any

from authentication.gql import AuthSchema
from thriftease_api.tests import TestGraphQL


class TestAuth(TestGraphQL, AuthSchema):
    @classmethod
    def sign_in(cls, gql: Any, email: str, password: str):
        response = gql(cls.mutation(cls.authSignIn(email, password)).render())
        content = json.loads(response.content)
        return dict(HTTP_AUTHORIZATION=f'JWT {content["data"]["authSignIn"]["token"]}')
