from collections import deque
from typing import Generic, Optional, TypeVar

from .types import ValidationError

T = TypeVar("T")


def build_error(errors: deque[str]) -> str:
    text = "\n"
    indent_level = 0

    # drain contents
    while errors:
        error = errors.popleft()
        if error == "indent":
            indent_level += 1
            continue
        elif error == "unindent":
            indent_level -= 1
            continue

        if indent_level:
            text += f"{'  ' * indent_level}• {error}\n"
        else:
            text += f"{error}\n"

    return text.rstrip()


class Result(Generic[T]):
    """Represents a result."""

    ok_data: Optional[T]
    errors: Optional["deque[str]"]  # deque is O(1)

    def __init__(self, okd: Optional[T], errors: Optional["deque[str]"]):
        self.ok_data = okd
        self.errors = errors

    @classmethod
    def Ok(cls, data: T) -> "Result[T]":
        return cls(data, None)

    @classmethod
    def Err(cls, *errors: str) -> "Result[T]":
        return cls(None, deque(errors))

    def unwrap(self) -> T:
        """Unwrap the OK data."""
        # cheap operation lmfao
        return self.ok_data  # type: ignore

    def unwrap_err(self) -> "deque[str]":
        """Unwrap the Err data."""
        # AGAIN. lmfao! you gotta be responsible.
        return self.errors  # type: ignore

    def is_ok(self) -> bool:
        """CALL."""
        return not self.errors

    def trace(self, upper: str) -> "Result[T]":
        if self.errors is not None:
            self.errors.appendleft("indent")
            self.errors.appendleft(upper)
            self.errors.append("unindent")

        return self

    @classmethod
    def trace_below(cls, upper: str, *items: str) -> "Result[T]":
        errors = deque(items)
        errors.appendleft("indent")
        errors.appendleft(upper)
        errors.append("unindent")

        return cls(okd=None, errors=errors)

    def raise_for_err(self) -> None:
        if self.is_ok():
            return

        error = build_error(self.unwrap_err())
        raise ValidationError(error)

    def __repr__(self) -> str:
        if self.is_ok():
            return f"Result.Ok({self.unwrap()!r})"
        else:
            return f"Result.Err({self.unwrap_err()!r})"
