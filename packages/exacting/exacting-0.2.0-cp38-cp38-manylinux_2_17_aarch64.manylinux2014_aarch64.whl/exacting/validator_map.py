import dataclasses
from dataclasses import is_dataclass
from weakref import ref

from types import NoneType, UnionType
from typing import Annotated, Any, Dict, Literal, Union, get_origin, get_type_hints

from .validators import (
    AnnotatedV,
    AnyV,
    BoolV,
    BytesV,
    DataclassV,
    DictV,
    FloatV,
    IntV,
    ListV,
    LiteralV,
    LooseDictV,
    LooseListV,
    NoneV,
    StrV,
    UnionV,
    Validator,
)
from .types import DataclassType

NONEV = NoneV()
STRV = StrV()
INTV = IntV()
FLOATV = FloatV()
BOOLV = BoolV()
BYTESV = BytesV()
LOOSE_LISTV = LooseListV()
LOOSE_DICTV = LooseDictV()
ANYV = AnyV()


def get_validator(typ: Any) -> Validator:
    if typ is None or isinstance(typ, NoneType) or typ is NoneType:
        return NONEV
    if typ is str:
        return STRV
    if typ is int:
        return INTV
    if typ is float:
        return FLOATV
    if typ is bool:
        return BOOLV
    if typ is bytes:
        return BYTESV
    if typ is list:
        return LOOSE_LISTV
    if typ is dict:
        return LOOSE_DICTV
    if typ is Any:
        return ANYV

    if is_dataclass(typ):
        return get_dc_validator(typ)

    origin = get_origin(typ)
    if origin is list:
        return ListV(get_validator(typ.__args__[0]))
    if origin is dict:
        return DictV(get_validator(typ.__args__[0]), get_validator(typ.__args__[1]))
    if origin is Union or origin is UnionType:
        return union(*typ.__args__)
    if origin is Literal:
        return LiteralV(typ.__args__)
    if origin is Annotated:
        return AnnotatedV(typ.__args__[0], typ.__metadata__)

    raise TypeError(
        f"Unknown type: {typ!r} (no type validator available at this moment)"
    )


def union(*items) -> Validator:
    if len(items) == 1:
        return get_validator(items[0])
    return UnionV(get_validator(items[0]), union(*items[1:]))


def get_map_for_dc(dc: DataclassType) -> Dict[str, Validator]:
    vmap = {}
    _FIELD = getattr(dataclasses, "_FIELD")
    type_hints = get_type_hints(dc)

    for field in dc.__dataclass_fields__.values():
        if getattr(field, "_field_type") is not _FIELD:
            raise NotImplementedError(
                "Currently, exacting only supports regular fields :(\n"
                f"...at field {field.name!r}, dataclass {dc!r}"
            )
        vmap[field.name] = get_validator(type_hints[field.name])

    return vmap


def get_dc_validator(dc: DataclassType) -> DataclassV:
    return DataclassV(ref(dc), get_map_for_dc(dc))
