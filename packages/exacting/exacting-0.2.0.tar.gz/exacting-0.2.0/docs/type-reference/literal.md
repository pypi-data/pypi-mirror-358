# Literal

Literal types tell `exacting` to check for value equality instead of types.

```python
from typing import Literal

Literal["Hello", b"beep", 123, True]
```

There can be multiple `Literal` items.

Literal types perform exactly as intended in `exacting`.
