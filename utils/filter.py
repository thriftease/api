from typing import Any, TypeVar

from django.db import models
from django.db.models import Q
from django.forms import ModelForm
from django_filters import FilterSet
from graphene import Enum, InputObjectType
from graphene_django.forms.mutation import fields_for_form

T = TypeVar("T", bound=InputObjectType)
T1 = TypeVar("T1", bound=Enum)


class FilterQueryInput(InputObjectType):
    filter_class: type[FilterSet] | None = None

    @classmethod
    def filter(
        cls, queryset: models.QuerySet[Any], **filters: Any
    ) -> models.QuerySet[Any]:
        return cls.filter_class(filters, queryset).qs  # type: ignore


class OrFilterSet(FilterSet):
    class Meta:
        abstract = True

    @property
    def qs(self):
        qs = self.queryset.all()
        if self.data:
            expr = None
            for k, v in self.data.items():
                if v is None:
                    continue
                # use or condition in chaining the filters, hence the '|' operator
                q = Q(**{k: v})
                expr = q if expr is None else expr | q
            qs = qs.filter(expr)
        return qs


def form_to_filter_input_class(
    name: str,
    form: ModelForm,
    type_: type[T] = InputObjectType,
    only_fields: set[str] = set(),
    exclude_fields: set[str] = set(),
) -> type[T]:
    return type(name, (type_,), fields_for_form(form, only_fields, exclude_fields))  # type: ignore


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
