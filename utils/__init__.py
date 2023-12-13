from typing import Any

from django.db import models


def formfield_extra_kwargs(**kwargs: dict[str, Any]):
    def formfield_callback(field: models.Field, **kw):
        nkw = {**kw}
        if field.name not in kwargs:
            return field.formfield(**nkw)
        nkw.update(kwargs[field.name])
        return field.formfield(**nkw)

    return formfield_callback
