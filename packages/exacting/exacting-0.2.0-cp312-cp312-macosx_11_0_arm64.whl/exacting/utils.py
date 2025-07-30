from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import MISSING, Field, _MISSING_TYPE
from typing import TypeVar, Union

unsafe_mode = ContextVar("unsafe_mode", default=False)


@contextmanager
def unsafe(on: bool = True, /):
    """Enable unsafe mode for unsafe operations.

    Example:
    ```python
    with unsafe():
        ...  # do stuff
    ```
    """

    token = unsafe_mode.set(on)
    try:
        yield
    finally:
        unsafe_mode.reset(token)


T = TypeVar("T")


def get_field_value(item: Union[T, _MISSING_TYPE], field: Field) -> T:
    if item is MISSING:
        if field.default is not MISSING:
            return field.default
        elif field.default_factory is not MISSING:
            return field.default_factory()
        else:
            raise KeyError(field.name)
    else:
        return item
