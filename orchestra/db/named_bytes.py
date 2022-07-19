import dataclasses
from typing import IO


@dataclasses.dataclass
class NamedBytes:
    name: str
    data: IO[bytes]
