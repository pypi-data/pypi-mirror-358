import uuid
from typing import Sequence, Optional, Any

import msgspec
import zmq
from zmq.asyncio import Context

from pydhara import TopicName
from pydhara.core.message_stream import MessageStream
from pydhara.core.serializer import Serializer

DEFAULT_READER_URL = "tcp://127.0.0.1:5555"
DEFAULT_WRITER_URL = "tcp://127.0.0.1:5556"


class ZMQBasicReaderWriterMessageStream(MessageStream):
    def __init__(
            self,
            reader_urls: Sequence[str] = (DEFAULT_READER_URL,),
            writer_urls: Sequence[str] = (DEFAULT_WRITER_URL,),
            unique_id: Optional[str] = None,
            bind_readers: bool = False,
            bind_writers: bool = False,
            serializer: Optional[Serializer] = None
    ):
        """
        ZeroMQ message stream with reader and writer sockets
        """
        self._id = unique_id or str(uuid.uuid4())
        self.reader_urls = reader_urls
        self.writer_urls = writer_urls
        self.bind_readers = bind_readers
        self.bind_writers = bind_writers

        self.context = None
        self.reader_socket: Optional[zmq.asyncio.Socket] = None
        self.writer_socket: Optional[zmq.asyncio.Socket] = None

        self.serializer = serializer or msgspec.json.Encoder()
        self.deserializer = msgspec.json.Decoder()

    def initialize(self):
        # Create a ZeroMQ context
        self.context = Context()

        # initializing writer/publisher socket
        self.writer_socket = self.context.socket(zmq.PUB)
        self.writer_socket.setsockopt(zmq.SNDHWM, 0)
        self.writer_socket.setsockopt(zmq.RCVHWM, 0)
        self.writer_socket.setsockopt(zmq.XPUB_NODROP, 1)
        for url in self.writer_urls:
            if self.bind_writers:
                self.writer_socket.bind(url)
            else:
                self.writer_socket.connect(url)

        # initializing reader
        self.reader_socket = self.context.socket(zmq.SUB)
        self.reader_socket.setsockopt(zmq.SNDHWM, 0)
        self.reader_socket.setsockopt(zmq.RCVHWM, 0)
        for url in self.reader_urls:
            if self.bind_readers:
                self.reader_socket.bind(url)
            else:
                self.reader_socket.connect(url)

    async def send(self, topic_name: TopicName, message: Any):
        return await self.writer_socket.send_multipart((topic_name.encode(), self.serializer.encode(message)))
        # return await self.writer_socket.send_multipart((topic_name.encode(), message))

    async def receive(self, block=True) -> (TopicName, Any):
        topic_name, data = await self.reader_socket.recv_multipart()
        return topic_name.decode(), self.deserializer.decode(data)
        # return topic_name.decode(), self.serializer.decode(data)

    async def finalize(self):
        if self.reader_socket is not None:
            self.reader_socket.close()

        if self.writer_socket is not None:
            self.writer_socket.close()

    def subscribe(self, topic: TopicName):
        self.reader_socket.setsockopt_string(zmq.SUBSCRIBE, topic)
