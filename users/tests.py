import json
from typing import Any

import pytest
from django.db import IntegrityError

from thriftease_api.tests import Schema
from users.models import User
from utils import ObjectDict

props = ObjectDict(
    email="test@email.com",
    password="@Password1234",
    given_name="Test",
    middle_name="",
    family_name="User",
    suffix="",
)


@pytest.mark.django_db
class TestUserModel:
    def init(self):
        self.model = User(**props)

    def test_create(self):
        self.init()
        self.model.save()

        # password hash
        assert self.model.password != props.password
        assert self.model.check_password(props.password)

        # email unique
        model = User(**props)
        with pytest.raises(IntegrityError) as err:
            model.save()
        assert err.match(r"UNIQUE.*email")

    def test_update(self):
        self.init()
        self.model.save()

        # password hash
        password = "@NewPassword1234"
        self.model.password = password
        self.model.save()
        assert self.model.password not in (password, props.password)
        assert not self.model.check_password(
            props.password
        ) and self.model.check_password(password)


class TestCreateUserMutation(Schema):
    def test_email(self, gql: Any):
        # required
        nprops = props.copy(email="")
        response = gql(self.mutation(self.createUser(*nprops.values())))
        content = json.loads(response.content)
        assert self.has_field_error(
            content, "createUser", "email", "This field is required."
        )

        # unique
        mutation = self.mutation(self.createUser(*props.values()))
        gql(mutation)
        response = gql(mutation)
        content = json.loads(response.content)
        assert self.has_field_error(
            content, "createUser", "email", "User with this Email already exists."
        )

        # valid
        nprops = props.copy(email="1234")
        response = gql(self.mutation(self.createUser(*nprops.values())))
        content = json.loads(response.content)
        assert self.has_field_error(
            content, "createUser", "email", "Enter a valid email address."
        )

    def test_password(self, gql: Any):
        # required
        nprops = props.copy(password="")
        response = gql(self.mutation(self.createUser(*nprops.values())))
        content = json.loads(response.content)
        assert self.has_field_error(
            content, "createUser", "password", "This field is required."
        )

        # at least 1 uppercase letter
        nprops = props.copy(password="a")
        response = gql(self.mutation(self.createUser(*nprops.values())))
        content = json.loads(response.content)
        assert self.has_field_error(
            content,
            "createUser",
            "password",
            "The password must contain at least one uppercase letter.",
        )

        # at least 1 lowercase letter
        nprops = props.copy(password="A")
        response = gql(self.mutation(self.createUser(*nprops.values())))
        content = json.loads(response.content)
        assert self.has_field_error(
            content,
            "createUser",
            "password",
            "The password must contain at least one lowercase letter.",
        )

        # at least 1 digit
        nprops = props.copy(password="aA")
        response = gql(self.mutation(self.createUser(*nprops.values())))
        content = json.loads(response.content)
        assert self.has_field_error(
            content,
            "createUser",
            "password",
            "The password must contain at least one digit.",
        )

        # at least 1 special character
        nprops = props.copy(password="aA1")
        response = gql(self.mutation(self.createUser(*nprops.values())))
        content = json.loads(response.content)
        assert self.has_field_error(
            content,
            "createUser",
            "password",
            "The password must contain at least one special character.",
        )

        # at least 7 characters
        nprops = props.copy(password="@aA1")
        response = gql(self.mutation(self.createUser(*nprops.values())))
        content = json.loads(response.content)
        assert self.has_field_error(
            content,
            "createUser",
            "password",
            "This password is too short. It must contain at least 7 characters.",
        )

        # complex
        nprops = props.copy(password="@aA1234")
        response = gql(self.mutation(self.createUser(*nprops.values())))
        content = json.loads(response.content)
        assert not self.has_field_error(content, "createUser", "password")

    def test_given_name(self, gql: Any):
        # required
        nprops = props.copy(given_name="")
        response = gql(self.mutation(self.createUser(*nprops.values())))
        content = json.loads(response.content)
        assert self.has_field_error(
            content, "createUser", "givenName", "This field is required."
        )

    def test_family_name(self, gql: Any):
        # required
        nprops = props.copy(family_name="")
        response = gql(self.mutation(self.createUser(*nprops.values())))
        content = json.loads(response.content)
        assert self.has_field_error(
            content, "createUser", "familyName", "This field is required."
        )
