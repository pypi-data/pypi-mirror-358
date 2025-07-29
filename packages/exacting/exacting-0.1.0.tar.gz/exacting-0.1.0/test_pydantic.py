import time
from typing import Union
from exacting import Exact

start = time.perf_counter()


class AnotherDataclass(Exact):
    id: int
    payload: str
    flag: bool
    checksum: bytes


class Config(Exact):
    retries: int
    timeout: float
    use_ssl: bool
    endpoint: str


class Metadata(Exact):
    tags: list[str]
    created_at: str
    version: Union[str, int]
    notes: Union[None, str, bytes]


class NestedLevelThree(Exact):
    data: list[AnotherDataclass]
    metadata: Metadata
    value: Union[int, float, str, bool]
    binary: bytes


class NestedLevelTwo(Exact):
    name: str
    configs: list[Config]
    children: list[NestedLevelThree]
    stats: dict[str, Union[int, float]]
    optional_info: Union[str, None, AnotherDataclass]


class NestedLevelOne(Exact):
    key: str
    nested: NestedLevelTwo
    mixed_list: list[Union[str, int, AnotherDataclass]]
    fallback: Union[AnotherDataclass, bool]
    retry_limit: int


class UltimateRoot(Exact):
    identifier: str
    deep: list[NestedLevelOne]
    extra: dict[str, list[AnotherDataclass]]
    settings: Config
    blob: Union[bytes, str, list[Union[str, bytes]]]
    flags: list[bool]


test_data = UltimateRoot(
    identifier="root-001",
    deep=[
        NestedLevelOne(
            key="level-one-a",
            nested=NestedLevelTwo(
                name="level-two-a",
                configs=[
                    Config(
                        retries=3,
                        timeout=1.5,
                        use_ssl=True,
                        endpoint="https://api.service",
                    ),
                    Config(
                        retries=5,
                        timeout=2.0,
                        use_ssl=False,
                        endpoint="http://backup.service",
                    ),
                ],
                children=[
                    NestedLevelThree(
                        data=[
                            AnotherDataclass(
                                id=1, payload="data-1", flag=True, checksum=b"\x01\x02"
                            ),
                            AnotherDataclass(
                                id=2, payload="data-2", flag=False, checksum=b"\x03\x04"
                            ),
                        ],
                        metadata=Metadata(
                            tags=["alpha", "beta"],
                            created_at="2023-04-01T12:00:00Z",
                            version="v1.0",
                            notes=b"Some binary notes",
                        ),
                        value=True,
                        binary=b"\x99\x88",
                    )
                ],
                stats={"requests": 1234, "load": 0.85},
                optional_info=AnotherDataclass(
                    id=99, payload="optional", flag=True, checksum=b"\xff"
                ),
            ),
            mixed_list=[
                "string",
                42,
                AnotherDataclass(id=77, payload="mixed", flag=False, checksum=b"\xab"),
            ],
            fallback=True,
            retry_limit=10,
        )
    ],
    extra={
        "groupA": [
            AnotherDataclass(id=3, payload="x", flag=True, checksum=b"\xde"),
            AnotherDataclass(id=4, payload="y", flag=False, checksum=b"\xad"),
        ]
    },
    settings=Config(
        retries=1, timeout=0.5, use_ssl=True, endpoint="https://fast.service"
    ),
    blob=[b"chunk1", b"chunk2", "fallback text"],
    flags=[True, False, True],
)

print((time.perf_counter() - start) * 1000, "ms")
