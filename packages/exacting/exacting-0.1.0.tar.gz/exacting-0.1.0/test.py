from exacting import Exact


class Woah(Exact):
    bruh: bool


class Place(Exact):
    name: str
    woah: Woah


place = Place(name="Freddy Fazbear's Pizza", woah=Woah(bruh=True))
archive = place.exact_as_json()
print(archive)  # b"\x00\x00\x00\x00name\xff..."

data = Place.exact_from_json(archive)
print(data)  # Place(name="Freddy Fazbear's Pizza")
