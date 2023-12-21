from typing import Any, Iterable

from django.core.paginator import Paginator
from graphene import Field, InputObjectType, Int, ObjectType


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
