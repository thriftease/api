from typing import Any, TypeVar

from django.forms import ModelForm
from graphene import Argument, Enum, List, NonNull

T1 = TypeVar("T1", bound=Enum)


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


def form_to_order_argument(form: type[ModelForm], *args: Any, **kwargs: Any):
    name: str = form._meta.model.__name__ + "OrderQueryInput"

    return Argument(List(NonNull(form_to_order_enum(name, form()))), *args, **kwargs)
