import json
from typing import Any, Callable, Dict, List, Type, TypeVar
from typing_extensions import Self, dataclass_transform

import dataclasses
from dataclasses import asdict, dataclass, is_dataclass

from .dc import get_etypes_for_dc
from .exacting import bytes_to_py, json_to_py, jsonc_to_py, py_to_bytes
from .types import NOTHING
from .etypes import DataclassType

T = TypeVar("T", bound=Type)


def get_exact_error_message(errors: List[str]) -> str:
    text = "\n"
    indents = 0
    for error in errors:
        if error == "indent":
            indents += 2
            text += " " * indents
            continue
        elif error == "unindent":
            indents -= 2
            text += " " * indents
            continue

        text += f"{error}\n{' ' * indents}"

    return text.rstrip()


def get_exact_init(dc: Type) -> Callable:
    etypes = get_etypes_for_dc(dc)
    setattr(dc, "__exact_types__", etypes)

    def init(self, **kwargs):
        for key, value in etypes.items():
            provided_value = kwargs.get(key, NOTHING)
            if provided_value is NOTHING:
                field = dc.__dataclass_fields__[key]
                if field.default is not dataclasses.MISSING:
                    provided_value = field.default
                elif field.default_factory is not dataclasses.MISSING:
                    provided_value = field.default_factory()
                else:
                    raise ValueError(
                        f"Error while validating dataclass {dc.__name__!r} at attribute {key!r}:\n"
                        "Field has no value provided."
                    )

            res = value.validate(provided_value)
            if res.has_error():
                raise TypeError(
                    get_exact_error_message(
                        [
                            f"Error while validating dataclass {dc.__name__!r} at attribute {key!r}:",
                            *res.errors,
                        ]
                    )
                )

            target = res.ok
            validators = dc.__dataclass_fields__[key].metadata.get(
                "exacting_validators"
            )
            if validators is not None:
                for validator in validators:
                    res_t = validator.validate(target)
                    if res_t.has_error():
                        raise TypeError(
                            get_exact_error_message(
                                [
                                    f"Error while validating dataclass {dc.__name__!r} at attribute {key!r} (field validator):",
                                    *res_t.errors,
                                ]
                            )
                        )
                    target = res_t.ok

            setattr(self, key, target)

        return None  # required!

    return init


def get_nonalias_and_dict(cls: Type["Exact"], data: dict) -> dict:
    types = getattr(cls, "__exact_types__")

    for field in cls.__dataclass_fields__.values():
        alias = field.metadata.get("exacting_alias")
        if alias is not None:
            item = data.pop(alias)
            data[field.name] = item

        etype = types[field.name]
        if isinstance(etype, DataclassType):
            dc = etype.item()
            if not dc:
                raise RuntimeError(
                    "Lost weakref over dataclass (internal, core.py, get_nonalias_and_dict())"
                )
            data[field.name] = dc(**data[field.name])

    return data


def transform_alias(cls: Type["Exact"], data: dict) -> dict:
    for field in cls.__dataclass_fields__.values():
        alias = field.metadata.get("exacting_alias")
        if alias is not None:
            item = data.pop(field.name)
            data[alias] = item

    return data


@dataclass_transform(kw_only_default=True)
class _ModelKwOnly: ...


class Exact(_ModelKwOnly):
    """
    All the APIs are prefixed with `exact_` to add clarity.
    """

    def __init_subclass__(cls) -> None:
        init = get_exact_init(dataclass(cls))
        setattr(cls, "__init__", init)

    def exact_as_dict(self) -> Dict[str, Any]:
        """(exacting) Creates a dictionary representation of this dataclass instance.

        Returns:
            dict[str, Any]

        Raises:
            AssertionError: Expected a dataclass
        """
        assert is_dataclass(self)
        data = asdict(self)
        return transform_alias(self.__class__, data)

    def exact_as_json(self) -> str:
        """(exacting) Creates a JSON representation of this dataclass instance.

        Returns:
            str

        Raises:
            AssertionError: Expected a dataclass
        """
        return json.dumps(self.exact_as_dict())

    def exact_as_bytes(self) -> bytes:
        """(exacting) Convert this instance of dataclass model into bytes."""
        return py_to_bytes(self.exact_as_dict())

    @classmethod
    def exact_from_json(cls, raw: str, *, strict: bool = True) -> Self:
        """(exacting) Initialize this dataclass model from JSON.

        When `strict` is set to `False`, exacting uses JSON5, allowing comments,
        trailing commas, object keys without quotes, single quoted strings and more.

        Example:

        ```python
        class Person(Exact):
            name: str
            age: int

        # strict mode (default)
        Person.exact_from_json(\"\"\"
        {
            "name": "Harry",
            "age": 23
        }
        \"\"\")

        # lenient :)
        Person.exact_from_json(\"\"\"
        {
            /*
                hell yeah!
            */
            name: "Walter",
            age: 23, // <- trailing commas? yeah!
        }
        \"\"\", strict=False)
        ```

        Args:
            raw (str): The raw JSON.
            strict (bool): Whether to use strict mode.
        """
        if strict:
            data = json_to_py(raw)
        else:
            data = jsonc_to_py(raw)

        return cls(**get_nonalias_and_dict(cls, data))

    @classmethod
    def exact_from_bytes(cls, raw: bytes) -> Self:
        data = bytes_to_py(raw)
        return cls(**get_nonalias_and_dict(cls, data))
