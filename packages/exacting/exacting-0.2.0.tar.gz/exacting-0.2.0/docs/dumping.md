# Dumping

Dump the model to a data format. Supports nested items.

## JSON

Everyone's favorite data type.

```python
from exacting import Exact

class Money(Exact):
    swag: bool

money = Money(swag=True)

json = money.exact_as_json()
print(json)  # {"swag": true}

data = Money.exact_from_json(json)
print(data)  # Money(swag=True)
```

Side note, you can actually load from JSON with comments (jsonc). Just disable strict mode via `strict=False`.

```python
json = """{
    "swag": /* false */ true, // yeah, trailing commas
}"""

data = Money.exact_from_json(json, strict=False)
print(data)  # Money(swag=True)
```


## Bytes

Exacting uses [rkyv](https://docs.rs/rkyv/latest/rkyv/) for serialization/deserialization.

```python
from exacting import Exact

class Place(Exact):
    name: str

place = Place(name="Freddy Fazbear's Pizza")
archive = place.exact_as_bytes()
print(archive)  # b"\x00\x00\x00\x00name\xff..."

data = Place.exact_from_bytes(archive)
print(data)  # Place(name="Freddy Fazbear's Pizza")
```
