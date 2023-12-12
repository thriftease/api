from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import identify_hasher
from django.db import models
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    def create_user(
        self, email: str, given_name: str, family_name: str, password: str | None = None
    ):
        if not email:
            raise ValueError(_("Users must have an email address"))

        user: User = self.model(
            email=self.normalize_email(email),
            given_name=given_name,
            family_name=family_name,
            password=password,
        )

        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, given_name: str, family_name: str, password: str | None = None
    ):
        user: User = self.create_user(
            email, given_name=given_name, family_name=family_name, password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=50)
    given_name = models.CharField(max_length=50)
    middle_name = models.CharField(blank=True, default="", max_length=50)
    family_name = models.CharField(max_length=50)
    suffix = models.CharField(blank=True, default="", max_length=20)

    is_admin = models.BooleanField(blank=True, default=False)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["given_name", "family_name"]

    objects = UserManager()

    @property
    def full_name(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        try:
            identify_hasher(self.password)
        except ValueError:
            self.set_password(self.password)
        return super().save(*args, **kwargs)

    def get_full_name(self):
        names = [self.given_name, self.family_name]
        if self.middle_name:
            names.insert(1, self.middle_name)
        if self.suffix:
            names.insert(len(names), self.suffix)
        return " ".join(names)

    def get_short_name(self):
        return self.given_name
