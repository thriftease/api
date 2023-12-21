import re
from collections.abc import Mapping
from typing import Any

from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext as _

from utils.filter import FilterQueryInput
from utils.paginator import PaginatorQueryInput


def formfield_extra_kwargs(**kwargs: dict[str, Any]):
    def formfield_callback(field: models.Field, **kw):
        nkw = {**kw}
        if field.name not in kwargs:
            return field.formfield(**nkw)
        nkw.update(kwargs[field.name])
        return field.formfield(**nkw)

    return formfield_callback


def validate_password(value: str | None = None):
    if isinstance(value, str):
        if not re.search(r"[a-z]", value):
            raise ValidationError(
                _("The password must contain at least one lowercase letter."),
                "password_no_lowercase",
            )
        if not re.search(r"[A-Z]", value):
            raise ValidationError(
                _("The password must contain at least one uppercase letter."),
                "password_no_uppercase",
            )
        if not re.search(r"[0-9]", value):
            raise ValidationError(
                _("The password must contain at least one digit."), "password_no_digit"
            )
        if not re.search(r'[!@#$%^&*()_+=\-[\]{};:\'",.<>/?]', value):
            raise ValidationError(
                _("The password must contain at least one special character."),
                "password_no_special",
            )
    if value is None or len(value) < 7:
        raise ValidationError(
            _(
                "This password is too short. It must contain at least "
                "%(min_length)d characters."
            ),
            "password_too_short",
            params={"min_length": 7},
        )


class ObjectDict(Mapping):
    def __init__(self, **kwargs: Any):
        for k, v in kwargs.items():
            self[k] = v

    def __getattr__(self, name) -> Any:
        return self.get(name, None)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]

    def __getitem__(self, key):
        return vars(self)[key]

    def __setitem__(self, key, value):
        vars(self)[key] = value

    def __delitem__(self, key):
        vars(self).pop(key)

    def __iter__(self):
        return iter(vars(self))

    def __len__(self):
        return len(vars(self))

    def __contains__(self, key):
        return key in vars(self)

    def copy(self, **kwargs: Any):
        kw = dict(vars(self))
        kw.update(kwargs)
        return type(self)(**kw)


def info_user_check(info, user):
    if info.context.user != user:
        raise Exception(_("You do not have permission to perform this action"))


def filter_order_paginate(
    queryset: models.QuerySet[Any],
    filter: FilterQueryInput | None = None,
    order: list[Any] | None = None,
    paginator: PaginatorQueryInput | None = None,
):
    data = queryset.order_by("id")
    if filter:
        data = filter.filter(data, **filter.__dict__)
    if order:
        data = data.order_by(*(e.value for e in order))
    paginator = paginator or PaginatorQueryInput()
    data, dpaginator = paginator.paginate(data)
    return data, dict(paginator=dpaginator)
