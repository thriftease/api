import json
from typing import Any

from authentication.gql import AuthSchema
from thriftease_api.tests import TestGraphQL
from users.models import User
from utils import ObjectDict


class TestAuth(TestGraphQL, AuthSchema):
    @classmethod
    def sign_in(cls, gql: Any, email: str, password: str):
        response = gql(cls.mutation(cls.authSignIn(email, password)).render())
        content = json.loads(response.content)
        return dict(HTTP_AUTHORIZATION=f'JWT {content["data"]["authSignIn"]["token"]}')

    @classmethod
    def sign_up(cls, gql: Any, **kwargs):
        response = gql(cls.mutation(cls.authSignUp(**kwargs)).render())
        content = json.loads(response.content)
        return content["data"]["authSignUp"]["data"]


class TestAuthSignUpMutation(TestAuth):
    def test(self, gql: Any):
        props = ObjectDict(
            email="test@email.com",
            password="@Password1234",
            given_name="Test",
            family_name="User",
        )
        self.sign_up(gql, **props)

        # created
        assert User.objects.filter(email=props.email).first()
