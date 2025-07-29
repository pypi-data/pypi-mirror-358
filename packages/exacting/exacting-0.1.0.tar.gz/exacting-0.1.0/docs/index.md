# Exacting

> *(adj.) making great demands on one's skill, attention, or other resources.*

`exacting` is a picky dataclass runtime utility collection, making sure all type annotations are followed.

Essentially... **THE** go-to option for dataclasses. heh.

**🔑 Key features**:

- **100% static typing.** Because I hate nothing too.
- Up to **10x faster** than [`pydantic`](https://pydantic.dev)! (Them: 60ms, us: 6~9ms)

![static typing](static-typing-proof.png)

<br />

**🛍️ Get `exacting`**:

=== "pip"

    ``` haskell
    pip install -U exacting
    ```

=== "uv"

    ``` haskell
    uv pip install -U exacting
    ```

=== "git"

    ``` shell
    git clone https://github.com/AWeirdDev/exacting
    ```

**🔥 Define some model**:

=== "Python 3.10+"

    ```python
    from exacting import Exact

    class Actor(Exact):
        name: str
        portrays: str

    class Show(Exact):
        name: str
        description: str | None
        actors: list[Actor]
    ```

=== "Python <= 3.9"

    ```python
    from typing import List, Optional
    from exacting import Exact

    class Actor(Exact):
        name: str
        portrays: str

    class Show(Exact):
        name: str
        description: Optional[str]
        actors: List[Actor]
    ```

**📦 Build 'em**:

```python
# (1) ✅ OK, exacting is happi
Show(
    name="Severance",
    description="great show",
    actors=[
        Actor(name="Adam Scott", portrays="Mark S."),
        Actor(name="Britt Lower", portrays="Helly R."),
    ]
)

# (2) ❌ Nuh-uh, exacting is angri
Show(
    name=123,
    description=False,
    actors=[
        "Walter White",
        "Jesse Pinkman"
    ]
)
```

??? failure "TypeError: Error while validating…"

    ``` python
    TypeError: 
    Error while validating dataclass 'Show' at attribute 'name':
    (isinstance) Expected <class 'str'>, got: <class 'int'>
    ```

Normally, when you use the parameters passed in example (2) above, the Python `dataclasses` library might as well just go with it, because they only put the additional **static typing** to the model, but not at **runtime**. Exacting makes sure that at both times, types are all enforced. It even gives you a detailed error message on where this occurs! (In a cool way)

It's worth noting that error generations are *lazy*, which means once Exacting finds out about a problem, it immediately raises a `TypeError` or `ValueError` (depending on the context) when we're at the high-level scale (say, a dataclass). This saves a lot of computation time if you have a larger model.

