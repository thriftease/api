from types import NoneType
from typing import Any, Literal, Self, Union


class Gql:
    indent = 2

    def render(self):
        return str(self)


Kwarg = str | int | tuple[Any, ...] | set[Any] | list[Any] | None


class GqlObject(Gql):
    def __init__(self, *args: str, **kwargs: Union[Kwarg, "GqlObject"]):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args: str, **kwargs: Union[Kwarg, dict[str, Any], "GqlObject"]):
        return self.copy(*args, **kwargs)

    @classmethod
    def to_key(cls, value: str):
        return "".join(
            map(
                lambda e: (e[1][0].lower() if e[0] == 0 else e[1][0].upper())
                + e[1][1:],
                enumerate(value.split("_")),
            )
        )

    @classmethod
    def to_value(cls, value: Any = ...):
        if value is Ellipsis:
            return ""
        elif isinstance(value, str):
            return f'"{value}"'
        elif value is None:
            return "null"
        return str(value)

    @classmethod
    def to_key_value(cls, key: str, *, value: Any = ...):
        key = cls.to_key(key)
        tvalue = cls.to_value(value)
        return (
            key
            if not tvalue
            else (
                f"{key} {tvalue}"
                if isinstance(value, cls) and not value.kwargs
                else f"{key}: {tvalue}"
            )
        )

    def copy(self, *args: str, **kwargs: Union[Kwarg, dict[str, Any], "GqlObject"]):
        skwargs: dict[str, Any] = {}
        for k, v in self.kwargs.items():
            nv: Union[Kwarg, dict[str, Any], "GqlObject"]
            if isinstance(v, (list, tuple, set)):
                nv = type(v)(v)
            elif isinstance(v, GqlObject):
                cv = kwargs.get(k, None)
                if isinstance(cv, dict):
                    nv = v.copy(**cv)
                    del kwargs[k]
                else:
                    nv = v.copy()
            else:
                nv = v
            skwargs[k] = nv
        skwargs.update(kwargs)
        return type(self)(*self.args, *args, **skwargs)

    def __str__(self):
        fmt = "{\n%s\n}"
        indent = " " * self.indent
        kvs = [
            *map(lambda e: self.to_key(e), self.args),
            *map(
                lambda e: self.to_key_value(e[0], value=e[1]),
                self.kwargs.items(),
            ),
        ]
        inside = "\n".join(kvs)
        if kvs:
            inside = "\n".join(map(lambda e: indent + e, inside.split("\n")))
        return fmt % inside

    def __repr__(self):
        return str(self)


class GqlArgument(GqlObject):
    def __init__(
        self, arg: dict[str, Any] | None = None, **kwargs: Union[Kwarg, "GqlObject"]
    ):
        kw = {}
        if arg is not None:
            kw.update(arg)
        kw.update(kwargs)
        super().__init__(**kw)


class GqlType(GqlObject):
    def __init__(self, *args: str, **kwargs: Self):
        super().__init__(*args, **kwargs)


class GqlAction(Gql):
    def __init__(
        self,
        name: str,
        argument: dict[str, Any] | GqlArgument | GqlType | None,
        type_: GqlType | None = None,
    ):
        self.name = name
        self.argument = GqlArgument()
        self.type = GqlType()
        if isinstance(argument, GqlArgument):
            self.argument = argument
        if isinstance(argument, (dict, NoneType)):
            self.argument = GqlArgument(argument)
        elif isinstance(argument, GqlType):
            self.type = argument
        if type_ is not None:
            self.type = type_

    def __str__(self):
        fmt = f"{self.name}"
        arg = str(self.argument)[2:-2]
        if arg:
            fmt += f"(\n{arg}\n)"
        fmt += " " + str(self.type)
        return fmt

    def __repr__(self):
        return str(self)


class GqlOperation(Gql):
    def __init__(
        self,
        type_: Literal["query", "mutation"],
        name: str | GqlAction | None,
        *actions: GqlAction,
    ):
        self.type = type_
        self.actions = list(actions)
        if not isinstance(name, GqlAction):
            self.name = name
        else:
            self.actions.insert(0, name)
            self.name = None

    def __str__(self):
        fmt = f"{self.type} {self.name + " " if self.name else ""}{{\n%s\n}}"
        indent = " " * self.indent
        acts = "\n".join(map(str, self.actions))
        if self.actions:
            acts = "\n".join(map(lambda e: indent + e, acts.split("\n")))
        fmt = fmt % acts
        return fmt

    def __repr__(self):
        return str(self)

    def add(self, *actions: GqlAction):
        self.actions.extend(actions)


class GqlQuery(GqlOperation):
    def __init__(self, name: str | GqlAction | None, *actions: GqlAction):
        super().__init__("query", name, *actions)


class GqlMutation(GqlOperation):
    def __init__(self, name: str | GqlAction | None, *actions: GqlAction):
        super().__init__("mutation", name, *actions)
