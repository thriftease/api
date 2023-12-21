import json
from typing import Any

import pytest
from django.db import IntegrityError

from authentication.tests import TestAuth
from thriftease_api.tests import TestGraphQL
from users.gql import UserSchema
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


class TestCreateUserMutation(TestGraphQL, UserSchema):
    def test_email(self, gql: Any):
        # required
        nprops = props.copy(email="")
        response = gql(self.mutation(self.createUser(**nprops)).render())
        content = json.loads(response.content)
        assert self.has_field_error(
            content, "createUser", "email", "This field is required."
        )

        # unique
        mutation = self.mutation(self.createUser(**props)).render()
        gql(mutation)
        response = gql(mutation)
        content = json.loads(response.content)
        assert self.has_field_error(
            content, "createUser", "email", "User with this Email already exists."
        )

        # valid
        nprops = props.copy(email="1234")
        response = gql(self.mutation(self.createUser(**nprops)).render())
        content = json.loads(response.content)
        assert self.has_field_error(
            content, "createUser", "email", "Enter a valid email address."
        )

    def test_password(self, gql: Any):
        # required
        nprops = props.copy(password="")
        response = gql(self.mutation(self.createUser(**nprops)).render())
        content = json.loads(response.content)
        assert self.has_field_error(
            content, "createUser", "password", "This field is required."
        )

        # at least 1 uppercase letter
        nprops = props.copy(password="a")
        response = gql(self.mutation(self.createUser(**nprops)).render())
        content = json.loads(response.content)
        assert self.has_field_error(
            content,
            "createUser",
            "password",
            "The password must contain at least one uppercase letter.",
        )

        # at least 1 lowercase letter
        nprops = props.copy(password="A")
        response = gql(self.mutation(self.createUser(**nprops)).render())
        content = json.loads(response.content)
        assert self.has_field_error(
            content,
            "createUser",
            "password",
            "The password must contain at least one lowercase letter.",
        )

        # at least 1 digit
        nprops = props.copy(password="aA")
        response = gql(self.mutation(self.createUser(**nprops)).render())
        content = json.loads(response.content)
        assert self.has_field_error(
            content,
            "createUser",
            "password",
            "The password must contain at least one digit.",
        )

        # at least 1 special character
        nprops = props.copy(password="aA1")
        response = gql(self.mutation(self.createUser(**nprops)).render())
        content = json.loads(response.content)
        assert self.has_field_error(
            content,
            "createUser",
            "password",
            "The password must contain at least one special character.",
        )

        # at least 7 characters
        nprops = props.copy(password="@aA1")
        response = gql(self.mutation(self.createUser(**nprops)).render())
        content = json.loads(response.content)
        assert self.has_field_error(
            content,
            "createUser",
            "password",
            "This password is too short. It must contain at least 7 characters.",
        )

        # complex
        nprops = props.copy(password="@aA1234")
        response = gql(self.mutation(self.createUser(**nprops)).render())
        content = json.loads(response.content)
        assert not self.has_field_error(content, "createUser", "password")

    def test_given_name(self, gql: Any):
        # required
        nprops = props.copy(given_name="")
        response = gql(self.mutation(self.createUser(**nprops)).render())
        content = json.loads(response.content)
        assert self.has_field_error(
            content, "createUser", "givenName", "This field is required."
        )

    def test_family_name(self, gql: Any):
        # required
        nprops = props.copy(family_name="")
        response = gql(self.mutation(self.createUser(**nprops)).render())
        content = json.loads(response.content)
        assert self.has_field_error(
            content, "createUser", "familyName", "This field is required."
        )


class TestUpdateUserMutation(TestGraphQL, UserSchema):
    def init(self):
        self.model = User(**props)
        self.model1 = User(**props.copy(email="test1@email.com"))

    def test(self, gql: Any):
        self.init()

        nprops = props.copy(
            id=1,
            password=None,
            given_name=None,
            middle_name=None,
            family_name=None,
            suffix=None,
        )
        del nprops.email
        # does not exist
        response = gql(self.mutation(self.updateUser(**nprops)).render())
        content = json.loads(response.content)
        assert self.has_error(
            content, "updateUser", "User matching query does not exist."
        )

        self.model.save()
        self.model1.save()
        headers = TestAuth.sign_in(gql, props.email, props.password)

        # updated other logged in
        nprops = nprops.copy(id=2, given_name="Testt", family_name="Userr")
        response = gql(
            self.mutation(self.updateUser(**nprops)).render(), headers=headers
        )
        content = json.loads(response.content)
        assert self.has_error(
            content, "updateUser", "You do not have permission to perform this action"
        )

        # updated logged in
        nprops = nprops.copy(id=1, given_name="Testt", family_name="Userr")
        response = gql(
            self.mutation(self.updateUser(**nprops)).render(), headers=headers
        )
        content = json.loads(response.content)
        data = content["data"]["updateUser"]["data"]
        assert (
            data["givenName"] == nprops.given_name
            and data["familyName"] == nprops.family_name
        )

        # updated not logged in
        nprops = nprops.copy(given_name="Testt", family_name="Userr")
        response = gql(self.mutation(self.updateUser(**nprops)).render())
        content = json.loads(response.content)
        assert self.has_error(
            content, "updateUser", "You do not have permission to perform this action"
        )


class TestDeleteUserMutation(TestGraphQL, UserSchema):
    def init(self):
        self.model = User(**props)
        self.model1 = User(**props.copy(email="test1@email.com"))

    def test(self, gql: Any):
        self.init()

        # does not exist
        response = gql(self.mutation(self.deleteUser(1)).render())
        content = json.loads(response.content)
        assert self.has_error(
            content, "deleteUser", "User matching query does not exist."
        )

        self.model.save()
        self.model1.save()
        headers = TestAuth.sign_in(gql, props.email, props.password)

        # deleted other logged in
        response = gql(
            self.mutation(self.deleteUser(self.model1.pk)).render(), headers=headers
        )
        content = json.loads(response.content)
        assert self.has_error(
            content, "deleteUser", "You do not have permission to perform this action"
        )

        # deleted logged in
        response = gql(
            self.mutation(self.deleteUser(self.model.pk)).render(), headers=headers
        )
        content = json.loads(response.content)
        assert content["data"]["deleteUser"]["data"]

        User(**props).save()

        # deleted not logged in
        response = gql(self.mutation(self.deleteUser(2)).render())
        content = json.loads(response.content)
        assert self.has_error(
            content, "deleteUser", "You do not have permission to perform this action"
        )
