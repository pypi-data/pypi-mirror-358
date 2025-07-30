import json
from dataclasses import MISSING, asdict, dataclass

from typing import Any, Dict, Type
from typing_extensions import Self, dataclass_transform

from .validators import DataclassV, Validator
from .validator_map import get_dc_validator
from .types import DataclassType
from .result import Result
from .utils import get_field_value, unsafe_mode

from .exacting import bytes_to_py, json_to_py, jsonc_to_py, py_to_bytes


def get_exact_init(dc: DataclassType):
    setattr(dc, "__validator__", get_dc_validator(dc))

    def init(self, **kwargs):
        for field in self.__dataclass_fields__.values():
            value = get_field_value(kwargs.get(field.name, MISSING), field)
            setattr(self, field.name, value)

        validator: Validator = getattr(dc, "__validator__")
        res: Result = validator.validate(self)
        res.raise_for_err()

        return None

    return init


def get_unsafe_init():
    @classmethod
    def __unsafe_init__(cls, **kwargs):
        if not unsafe_mode.get():
            raise RuntimeError("Scope is not in unsafe(), canceled operation")

        item = cls.__new__(cls)
        for field in cls.__dataclass_fields__.values():
            setattr(
                item,
                field.name,
                get_field_value(kwargs.get(field.name, MISSING), field),
            )
        return item

    return __unsafe_init__


@dataclass_transform(kw_only_default=True)
def exact(cls: Type) -> DataclassType:
    dc = dataclass(kw_only=True)(cls)
    unsafe_init = get_unsafe_init()
    setattr(dc, "__unsafe_init__", unsafe_init)

    exact_init = get_exact_init(dc)
    setattr(dc, "__init__", exact_init)

    return dc


class _Internals:
    __validator__: DataclassV

    @classmethod
    def __unsafe_init__(cls, **kwargs) -> Self:
        """Unsafely initialize the dataclass with no-brain filling.

        Example:

        ```python
        from exacting import unsafe

        with unsafe():
            SomeDataclass.__unsafe_init__(**kwargs)
        ```
        """
        raise NotImplementedError()


@dataclass_transform(kw_only_default=True)
class _Dc: ...


class Exact(_Dc, _Internals):
    def __init_subclass__(cls) -> None:
        exact(cls)

    def exact_as_dict(self) -> Dict[str, Any]:
        """Get this model instance as a dictionary."""
        return asdict(self)

    def exact_as_json(self) -> str:
        """Get this model instance as JSON."""
        return json.dumps(self.exact_as_dict())

    def exact_as_bytes(self) -> bytes:
        """Get this model instance as bytes with `rkyv`.

        This may **not** be super efficient.
        """
        return py_to_bytes(self.exact_as_dict())

    @classmethod
    def exact_from_dict(cls, d: Dict[str, Any]) -> Self:
        """(exacting) Get this model from a raw dictionary."""
        res = cls.__validator__.validate(d, from_dict=True)
        res.raise_for_err()
        return res.unwrap()

    @classmethod
    def exact_from_json(cls, raw: str, /, *, strict: bool = True) -> Self:
        """(exacting) Get this model from raw JSON.

        When strict mode is set to `False`, you could use JSON with comments
        and more modern features.

        Args:
            raw (str): The raw JSON data.
            strict (bool): Whether to turn strict mode on.
        """
        if strict:
            d = json_to_py(raw)
        else:
            d = jsonc_to_py(raw)

        res = cls.__validator__.validate(d, from_dict=True)
        res.raise_for_err()
        return res.unwrap()

    @classmethod
    def exact_from_bytes(cls, raw: bytes) -> Self:
        """(exacting) Get this model from raw bytes."""
        d = bytes_to_py(raw)
        res = cls.__validator__.validate(d, from_dict=True)
        res.raise_for_err()
        return res.unwrap()
