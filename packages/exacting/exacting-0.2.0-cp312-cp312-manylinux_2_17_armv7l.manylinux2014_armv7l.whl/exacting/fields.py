import dataclasses as std_dc
from dataclasses import MISSING

from typing import Any, Callable, List, Type, TypeVar, Union

from .validators import Validator, MinMaxV, RegexV
from .types import _Optional

T = TypeVar("T")


class ExactField:
    validators: List[Validator]

    def __init__(self, validators: List[Validator]):
        self.validators = validators


def field(
    typ: _Optional[Type[T]] = MISSING,
    *,
    default: _Optional[T] = MISSING,
    default_factory: _Optional[Callable[[], T]] = MISSING,
    hash: _Optional[bool] = MISSING,
    regex: _Optional[str] = MISSING,
    minv: _Optional[Union[int, float]] = MISSING,
    maxv: _Optional[Union[int, float]] = MISSING,
) -> Any:
    validators = []
    if regex is not MISSING:
        validators.append(RegexV(regex))

    if minv is not MISSING or maxv is not MISSING:
        validators.append(MinMaxV(minv, maxv))

    if default is not MISSING:
        return std_dc.field(
            default=default,
            metadata={"exact": ExactField(validators)},
            hash=None if hash is MISSING else hash,
        )
    elif default_factory is not MISSING:
        return std_dc.field(
            default_factory=default_factory,
            metadata={"exact": ExactField(validators)},
            hash=None if hash is MISSING else hash,
        )
    else:
        return std_dc.field(
            metadata={"exact": ExactField(validators)},
            hash=None if hash is MISSING else hash,
        )
