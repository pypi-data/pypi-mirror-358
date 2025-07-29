"""Types for `exacting`.

A variable that's prefixed with `e` followed by a built-in Python type is
inherited from `BaseType`, which supports validation via `validate()`.

The `expect()` function is also available if you'd like to make a custom type.
"""

from dataclasses import is_dataclass

import typing
from typing import Any, Generic, Type, TypeVar
from weakref import ReferenceType

from .types import Dataclass

T = TypeVar("T")
K = TypeVar("K")


class TypeResult(Generic[T]):
    __slots__ = ("ok", "errors")

    ok: typing.Optional[T]
    errors: typing.List[
        typing.Union[str, typing.Literal["indent"], typing.Literal["unindent"]]
    ]

    def __init__(
        self,
        *,
        ok: typing.Optional[T] = None,
        errors: typing.Optional[
            typing.List[
                typing.Union[str, typing.Literal["indent"], typing.Literal["unindent"]]
            ]
        ] = None,
    ):
        self.ok = ok
        self.errors = errors or []

    def has_error(self):
        return bool(self.errors)


def unwrap(o: typing.Optional[T]) -> T:
    return o  # type: ignore


def expect(t: Type[T], x: Any) -> TypeResult[T]:
    """Expect an instance of a type.

    Args:
        t: The type object.
        x: Any value to test.
    """
    if isinstance(x, t):
        return TypeResult(ok=x)
    else:
        return TypeResult(errors=[f"(isinstance) Expected {t}, got: {type(x)!r}"])


class BaseType(Generic[T]):
    def __init__(self): ...
    def validate(self, x: Any) -> TypeResult[T]:
        """Validates the type."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return "BaseType"


class StrType(BaseType[str]):
    def validate(self, x: Any) -> TypeResult[str]:
        return expect(str, x)

    def __repr__(self) -> str:
        return "str"


estr = StrType()


class IntType(BaseType[int]):
    def validate(self, x: Any) -> TypeResult[int]:
        return expect(int, x)

    def __repr__(self) -> str:
        return "int"


eint = IntType()


class BoolType(BaseType[bool]):
    def validate(self, x: Any) -> TypeResult[bool]:
        return expect(bool, x)

    def __repr__(self) -> str:
        return "bool"


ebool = BoolType()


class FloatType(BaseType[float]):
    def validate(self, x: Any) -> TypeResult[float]:
        return expect(float, x)

    def __repr__(self) -> str:
        return "float"


efloat = FloatType()


class BytesType(BaseType[bytes]):
    def validate(self, x: Any) -> TypeResult[bytes]:
        return expect(bytes, x)

    def __repr__(self) -> str:
        return "bytes"


ebytes = BytesType()


class ListType(BaseType[typing.List[T]]):
    target: BaseType[T]

    def __init__(self, target: BaseType[T]):
        self.target = target

    def validate(self, x: Any) -> TypeResult[typing.List[T]]:
        res = expect(list, x)
        if res.has_error():
            return res

        array = unwrap(res.ok)

        for idx, item in enumerate(array):
            result = self.target.validate(item)
            if result.has_error():
                return TypeResult(
                    errors=[
                        f"During validation of list[{self.target!r}] at item index {idx}, a type error occurred:",
                        "indent",
                        *result.errors,
                        "unindent",
                    ]
                )

            array[idx] = unwrap(result.ok)

        return TypeResult(ok=array)

    def __repr__(self) -> str:
        return f"list[{self.target!r}]"


class NoneType(BaseType[None]):
    def validate(self, x: Any) -> TypeResult[None]:
        if x is not None:
            return TypeResult(errors=[f"Expected None, got: {type(x)}"])
        return x

    def __repr__(self) -> str:
        return "None"


enone = NoneType()


class AnyType(BaseType[Any]):
    def validate(self, x: Any) -> Any:
        return TypeResult(ok=x)


eany = AnyType()


class DictType(BaseType[typing.Dict[K, T]]):
    k_target: BaseType[K]
    v_target: BaseType[T]

    def __init__(self, k_target: BaseType[K], v_target: BaseType[T]):
        self.k_target = k_target
        self.v_target = v_target

    def validate(self, x: Any) -> TypeResult[typing.Dict[K, T]]:
        res = expect(dict, x)
        if res.has_error():
            return res

        dictionary = unwrap(res.ok)

        for key, value in dictionary.items():
            result = self.k_target.validate(key)
            if result.has_error():
                return TypeResult(
                    errors=[
                        f"During validation of dict[{self.k_target!r}] at key {key!r}, a type error occurred:",
                        "indent",
                        *result.errors,
                        "unindent",
                    ]
                )

            k = unwrap(result.ok)

            result2 = self.v_target.validate(value)
            if result2.has_error():
                return TypeResult(
                    errors=[
                        f"During validation of dict[{self.v_target!r}] at the *value* paired with the key {key!r}, a type error occurred:",
                        "indent",
                        *result2.errors,
                        "unindent",
                    ]
                )

            v = unwrap(result2.ok)

            dictionary[k] = v

        return TypeResult(ok=dictionary)

    def __repr__(self) -> str:
        return f"dict[{self.k_target!r}, {self.v_target!r}]"


class UnionType(BaseType[typing.Union[K, T]]):
    a: BaseType[K]
    b: BaseType[T]

    def __init__(self, a: BaseType[K], b: BaseType[T]):
        self.a = a
        self.b = b

    def validate(self, x: Any) -> TypeResult[typing.Union[K, T]]:
        result = self.a.validate(x)
        if result.has_error():
            messages = result.errors
        else:
            return TypeResult(ok=unwrap(result.ok))

        result2 = self.b.validate(x)
        if result2.has_error():
            return TypeResult(
                errors=[
                    f"Expected either type {self.a!r} or type {self.b!r}.\n",
                    f"• Attempted {self.a!r}, got:",
                    "indent",
                    *messages,
                    "unindent",
                    f"• Attempted {self.b!r}, got:",
                    "indent",
                    *result2.errors,
                    "unindent",
                ],
            )
        else:
            return TypeResult(ok=unwrap(result2.ok))

    def __repr__(self) -> str:
        return f"{self.a!r} | {self.b!r}"


def union(*items: BaseType) -> BaseType:
    """Creates a union type.

    Example:

    ```python
    union(estr, eint, ebool)
    ```
    """
    assert len(items) > 0

    if len(items) > 1:
        return UnionType(items[0], union(*items[1:]))
    else:
        return items[0]


class DataclassType(BaseType[Dataclass]):
    item: "ReferenceType[Type[Dataclass]]"
    target: typing.Dict[str, BaseType]

    def __init__(self, item: ReferenceType, target: typing.Dict[str, BaseType]):
        self.item = item
        self.target = target

    def validate(self, x: Any) -> TypeResult[Any]:
        item = self.item()
        if item is None:
            return TypeResult(
                errors=[
                    "Lost weakref over self.item (internal, etypes.py, DataclassType, validate())"
                ]
            )
        if not is_dataclass(x):
            return TypeResult(
                errors=[f"Expected dataclass instance ({item!r}), got: {x!r}"]
            )

        for name, etype in self.target.items():
            item = getattr(x, name)
            res = etype.validate(item)

            if res.has_error():
                return TypeResult(
                    errors=[
                        f"During validation of dataclass {item!r} at attribute {name!r}, a type error occurred:",
                        "indent",
                        *res.errors,
                        "unindent",
                    ]
                )

            setattr(x, name, res.ok)

        return TypeResult(ok=x)

    def __repr__(self) -> str:
        return repr(self.item() or "_LostRefDataclass")


class AnnotatedType(BaseType[Any]):
    target: BaseType
    metadata: typing.List[Any]

    def __init__(self, target: BaseType, items: typing.List[Any]):
        self.target = target
        self.metadata = items

    def validate(self, x: Any) -> TypeResult[Any]:
        return self.target.validate(x)


class LiteralType(BaseType):
    targets: typing.List[Any]

    def __init__(self, targets: typing.List[Any]):
        self.targets = targets

    def validate(self, x: Any) -> TypeResult:
        for item in self.targets:
            if x == item:
                return TypeResult(ok=x)

        return TypeResult(errors=[f"Cannot find item matching {self!r}"])

    def __repr__(self) -> str:
        return f"literal[{', '.join(repr(i) for i in self.targets)}]"
