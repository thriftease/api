from typing import Any

from django.core.paginator import Paginator
from django.db import models
from graphene import Boolean, Field, InputObjectType, Int, ObjectType


def formfield_extra_kwargs(**kwargs: dict[str, Any]):
    def formfield_callback(field: models.Field, **kw):
        nkw = {**kw}
        if field.name not in kwargs:
            return field.formfield(**nkw)
        nkw.update(kwargs[field.name])
        return field.formfield(**nkw)

    return formfield_callback


class PageType(ObjectType):
    count = Int(default_value=0)
    num_pages = Int(default_value=1)
    has_next = Boolean(default_value=False)
    has_previous = Boolean(default_value=False)
    has_other_pages = Boolean(default_value=False)
    next_page_number = Int()
    previous_page_number = Int()
    start_index = Int()
    end_index = Int()
    number = Int(default_value=1)


class PaginatorQueryInput(InputObjectType):
    per_page = Int(default_value=10)
    page = Int(default_value=1)

    def paginate(self, objects: Any):
        paginator = Paginator(objects, self.per_page)  # type: ignore
        print("Page", self.page, self.per_page)
        page = paginator.page(self.page)  # type: ignore
        fields = list(PageType._meta.fields.keys())
        kwargs = {}
        fields.remove("count")
        kwargs["count"] = paginator.count
        fields.remove("num_pages")
        kwargs["num_pages"] = paginator.num_pages
        kwargs.update(
            {
                k: getattr(page, k)()
                if callable(getattr(page, k))
                else getattr(page, k)
                for k in fields
            }  # type: ignore
        )
        page_type = PageType(**kwargs)
        return page.object_list, page_type


class PaginatorQueryPayload(ObjectType):
    page = Field(PageType)
