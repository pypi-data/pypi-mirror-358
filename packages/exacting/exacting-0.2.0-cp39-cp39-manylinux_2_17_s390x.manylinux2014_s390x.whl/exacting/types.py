import dataclasses as std_dc

from typing import Any, Dict, Protocol, Type, TypeVar, Union


class Dataclass(Protocol):
    __dataclass_fields__: Dict[str, std_dc.Field]


DataclassType = Union[Type[Dataclass], Any]


class _Indexable:
    def __getitem__(self, k: str): ...
    def __setitem__(self, k: str, data: Any): ...
    def get(self, k: str) -> Any: ...
    def as_dict(self) -> dict: ...
    def as_dc(self) -> Dataclass: ...


class _DefinitelyDict(_Indexable):
    def __init__(self, d: Dict):
        self.data = d

    def get(self, k: str):
        return self.data.get(k, std_dc.MISSING)

    def __getitem__(self, k: str):
        return self.data[k]

    def __setitem__(self, k: str, data: Any):
        self.data[k] = data

    def as_dict(self) -> dict:
        return self.data

    def as_dc(self) -> Dataclass:
        raise TypeError("This indexable is not a dataclass but a dict")


class _DefinitelyDataclass(_Indexable):
    def __init__(self, dc: Dataclass):
        self.dc = dc

    def get(self, k: str):
        return getattr(self.dc, k, std_dc.MISSING)

    def __getitem__(self, k: str):
        return getattr(self.dc, k)

    def __setitem__(self, k: str, data: Any):
        setattr(self.dc, k, data)

    def as_dict(self):
        raise TypeError("This indexable is not a dict but a dataclass")

    def as_dc(self) -> Dataclass:
        return self.dc


def indexable(item: Any) -> "_Indexable":
    if isinstance(item, dict):
        return _DefinitelyDict(item)
    else:
        return _DefinitelyDataclass(item)


class ValidationError(RuntimeError):
    """Validation error for `exacting`."""


T = TypeVar("T")
_Optional = Union[T, std_dc._MISSING_TYPE]
