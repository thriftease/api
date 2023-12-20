import re
from collections.abc import Mapping
from typing import Any, Iterable, TypeVar

from django.core.paginator import Paginator
from django.db import models
from django.forms import ModelForm, ValidationError
from django.utils.translation import gettext as _
from django_filters import FilterSet
from graphene import (
    Argument,
    Enum,
    Field,
    InputObjectType,
    Int,
    List,
    NonNull,
    ObjectType,
)
from graphene_django.forms.mutation import fields_for_form

T = TypeVar("T", bound=InputObjectType)
T1 = TypeVar("T1", bound=Enum)


def form_to_filter_input_class(
    name: str,
    form: ModelForm,
    type_: type[T] = InputObjectType,
    only_fields: set[str] = set(),
    exclude_fields: set[str] = set(),
) -> type[T]:
    return type(name, (type_,), fields_for_form(form, only_fields, exclude_fields))  # type: ignore


def form_to_order_enum(
    name: str,
    form: ModelForm,
    type_: type[T1] = Enum,
    only_fields: set[str] = set(),
    exclude_fields: set[str] = set(),
):
    attrs = []
    for k in form.fields:
        if (only_fields and k not in only_fields) or k in exclude_fields:
            continue
        attrs.append((f"{k.upper()}_ASC", f"{k}"))
        attrs.append((f"{k.upper()}_DESC", f"-{k}"))
    return type_(name, attrs)


class FilterQueryInput(InputObjectType):
    filter_class: type[FilterSet] | None = None

    @classmethod
    def filter(
        cls, queryset: models.QuerySet[Any], **filters: Any
    ) -> models.QuerySet[Any]:
        return cls.filter_class(filters, queryset).qs  # type: ignore


def filter_to_filter_input_class(
    filter: type[FilterSet],
    name: str | None = None,
    only_fields: set[str] = set(),
    exclude_fields: set[str] = set(),
):
    if not name:
        name = filter.__name__ + "QueryInput"
    cls = form_to_filter_input_class(
        name, filter().get_form_class()(), FilterQueryInput, only_fields, exclude_fields
    )
    cls.filter_class = filter
    return cls


def form_to_order_argument(form: type[ModelForm], *args: Any, **kwargs: Any):
    name: str = form._meta.model.__name__ + "OrderQueryInput"

    return Argument(List(NonNull(form_to_order_enum(name, form()))), *args, **kwargs)


def formfield_extra_kwargs(**kwargs: dict[str, Any]):
    def formfield_callback(field: models.Field, **kw):
        nkw = {**kw}
        if field.name not in kwargs:
            return field.formfield(**nkw)
        nkw.update(kwargs[field.name])
        return field.formfield(**nkw)

    return formfield_callback


def set_values(input_object: InputObjectType):
    defval = "default_value"
    for field in input_object._meta.fields:
        rfield = getattr(input_object, field)
        if defval in rfield.kwargs:
            setattr(
                input_object,
                field,
                input_object.kwargs.get(field, rfield.kwargs[defval]),
            )


class PageType(ObjectType):
    previous = Int()
    current = Int(default_value=1, required=True)
    next = Int()


class PaginatorType(ObjectType):
    per_page = Int(default_value=1, required=True)
    items = Int(default_value=0, required=True)
    pages = Int(default_value=1, required=True)
    page = Field(PageType, required=True)


class PaginatorQueryInput(InputObjectType):
    per_page = Int(default_value=10)
    page = Int(default_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_values(self, **kwargs)

    def paginate(self, objects: Iterable[Any]):
        paginator = Paginator(objects, max(self.per_page, 1))  # type: ignore
        page = paginator.get_page(min(max(self.page, 1), paginator.num_pages))  # type: ignore
        kwargs = dict(
            per_page=paginator.per_page,
            items=paginator.count,
            pages=paginator.num_pages,
            page=PageType(),
        )
        pkwargs = dict(
            previous=page.previous_page_number() if page.has_previous() else None,
            current=page.number,
            next=page.next_page_number() if page.has_next() else None,
        )
        kwargs["page"] = PageType(**pkwargs)
        paginator_type = PaginatorType(**kwargs)
        return page.object_list, paginator_type


class PaginatorQueryPayload(ObjectType):
    paginator = Field(PaginatorType)


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
