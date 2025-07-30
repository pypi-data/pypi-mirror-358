# Union

The union type allows you to have multiple choices of types.

=== "Python 3.10+"

    ```python
    A | B | C
    ```

=== "Python <= 3.9"

    ```python
    from typing import Union

    Union[A, B, C]
    ```

Union types perform exactly as intended in `exacting`.
