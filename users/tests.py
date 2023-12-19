import pytest
from django.db import IntegrityError

from users.models import User


@pytest.mark.django_db
class TestUserModel:
    props = dict(
        email="test@email.com",
        password="@Password1234",
        given_name="Test",
        middle_name="",
        family_name="User",
        suffix="",
    )

    def init(self):
        self.model = User(**self.props)

    def test_create(self):
        self.init()
        self.model.save()

        # test password
        assert self.model.password != self.props["password"]
        assert self.model.check_password(self.props["password"])

        # test email uniqueness
        model = User(**self.props)
        with pytest.raises(IntegrityError) as err:
            model.save()
        assert err.match(r"UNIQUE.*email")

    def test_update(self):
        self.init()
        self.model.save()

        # test password
        password = "@NewPassword1234"
        self.model.password = password
        self.model.save()
        assert self.model.password not in (password, self.props["password"])
        assert not self.model.check_password(
            self.props["password"]
        ) and self.model.check_password(password)
