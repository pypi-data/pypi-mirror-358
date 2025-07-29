from typing import Any


def json_to_py(json: str) -> Any:
    """Convert raw JSON to Python data types.

    Args:
        json (str): The JSON data.
    """


def jsonc_to_py(json: str) -> Any:
    """Convert raw JSON to Python data bytes while allowing comments,
    trailing commas, object keys without quotes, single quoted strings and more.

    Uses JSON5:
    > JSON5 is a superset of JSON with an expanded syntax including some productions from ECMAScript 5.1.

    Args:
        json (str): The JSONC data.
    """


class Regex:
    def __init__(self, m: str): ...
    def validate(self, input: str) -> bool:
        """Checks if `input` matches the regex.

        Args:
            input (str): The input.

        Raises:
            RuntimeError: Rust-side error.
        """


def py_to_bytes(data: Any) -> bytes:
    """Convert Python data to bytes."""


def bytes_to_py(data: bytes) -> Any:
    """Convert bytes to Python data."""
