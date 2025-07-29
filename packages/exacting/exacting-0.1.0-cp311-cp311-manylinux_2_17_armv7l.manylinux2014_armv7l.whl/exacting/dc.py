import dataclasses
from dataclasses import is_dataclass

import types as std_types
import typing
from typing import Any, Dict, Type, Union, get_origin, get_type_hints

from weakref import ref

from .types import Dataclass
from .etypes import (
    AnnotatedType,
    BaseType,
    DataclassType,
    DictType,
    ListType,
    LiteralType,
    eany,
    enone,
    estr,
    ebool,
    eint,
    efloat,
    ebytes,
    union,
)


def get_etype_from_type(typ: Type) -> BaseType:
    # standard types
    if typ is None or typ is std_types.NoneType:
        return enone
    if typ is str:
        return estr
    if typ is int:
        return eint
    if typ is bool:
        return ebool
    if typ is float:
        return efloat
    if typ is bytes:
        return ebytes
    if typ is typing.Any:
        return eany

    if is_dataclass(typ):
        rf = ref(typ)
        return DataclassType(rf, get_etypes_for_dc(typ))

    origin = get_origin(typ)
    if origin is typing.Union or origin is std_types.UnionType:
        return union(*(get_etype_from_type(arg) for arg in typ.__args__))
    elif origin is list:
        return ListType(get_etype_from_type(typ.__args__[0]))
    elif origin is dict:
        return DictType(
            get_etype_from_type(typ.__args__[0]), get_etype_from_type(typ.__args__[1])
        )
    elif origin is typing.Annotated:
        return AnnotatedType(
            get_etype_from_type(typ.__args__[0]), list(typ.__metadata__)
        )
    elif origin is typing.Literal:
        return LiteralType(list(typ.__args__))

    raise TypeError(f"Unknown type: {typ!r}")


def get_etypes_for_dc(dc: Union[Type[Dataclass], Any]) -> Dict[str, BaseType]:
    """Attempts to get the exacting validator types."""
    assert is_dataclass(dc), "Expected a dataclass"

    _FIELD = getattr(dataclasses, "_FIELD")

    etypes = {}
    types = get_type_hints(dc)
    for name, field in dc.__dataclass_fields__.items():
        if getattr(field, "_field_type", _FIELD) is not _FIELD:
            continue

        etypes[name] = get_etype_from_type(types[name])

    return etypes
