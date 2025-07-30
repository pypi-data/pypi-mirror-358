from typing import Protocol, Any


class Serializer(Protocol):
    def encode(self, message: Any) -> bytes:
        pass

    def decode(self, data: bytes) -> Any:
        pass
