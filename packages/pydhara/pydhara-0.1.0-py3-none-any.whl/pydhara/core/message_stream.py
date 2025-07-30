from typing import Protocol, Dict, Any, TypeVar

from pydhara import TopicName


class MessageStream(Protocol):
    """base class to handing sending and receiving messages based on topics"""

    _id: str

    @classmethod
    def from_config(cls, cfg: Dict[str, Any]) -> "MessageStream":
        pass

    def initialize(self):
        pass

    def subscribe(self, topic: TopicName):
        pass

    async def send(self, topic_name: TopicName, message: Any):
        pass

    async def receive(self, block=True) -> [TopicName, Any]:
        pass

    async def close(self):
        pass


MessageStreamInitializer = TypeVar("MessageStreamInitializer", bound=MessageStream)
