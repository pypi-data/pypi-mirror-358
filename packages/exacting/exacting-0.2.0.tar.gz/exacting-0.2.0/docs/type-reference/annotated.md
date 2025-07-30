# Annotated

Annotated types allow you to annotate any value onto the type field.

```python
from typing import Annotated

#         type, metadata.......
Annotated[str,  "any data", 123]
```

`exacting` only checks for the type, not the metadata.

For future development of `exacting`, it might be used as a doc field.
