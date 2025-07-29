# exacting
> *(adj.) making great demands on one's skill, attention, or other resources.*

`exacting` is a picky dataclass runtime utility collection, making sure all type annotations are followed.

Essentially... **THE** go-to option for dataclasses. heh.

**Key features**:

- **100% static typing.** Because I hate nothing too.
- Up to **10x faster** than [`pydantic`](https://pydantic.dev)! (Them: 60ms, us: 6~9ms)

## Examples
```python
from exacting import Exact

class Person(Exact):
    name: str
    age: int

Person(name="John", age=123)  # Ok!

Person(name="John", age=1.23)
#                       ^^^^
# See the curly underlines? Normally, they pop out 
# from your code editor from the language server, 
# but types aren't strict in **runtime**, which means
# this expression is completely valid if you used 
# @dataclass instead.
# Thankfully, `exacting` gives us an error message:
# 
# TypeError:
# During validation of dataclass 'Person' at attribute 'age', a type error occurred:
# (isinstance) Expected <class 'int'>, got: <class 'float'>
```

Also, you can type anything! Almost.

```python
@exact
class Stuff:
    apple: Optional[str]
    banana: str | int | bool

# ...they all work!
```

***

WIP. More APIs soon.

(c) 2025, AWeirdDev
