import asyncio
import uuid
from asyncio import Task
from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Optional, Any, Dict, Callable, Sequence

from loguru import logger

from pydhara import SystemCommand, TopicName, SYSTEM_COMMAND_TOPIC, MESSAGE_STREAM_CATALOG
from pydhara.core.message_stream import MessageStream


@dataclass(slots=True)
class FieldInfo:
    label: str
    value: Any
    # dtype: Any = str
    editable: bool = True

    def to_dict(self):
        return {
            "label": self.label,
            # "dtype": self.dtype.__name__,
            "value": self.value,
            "editable": self.editable,
        }

    @classmethod
    def from_dict(cls, data):
        # dtype = globals()[data["dtype"]]
        return cls(
            label=data["label"],
            # dtype=dtype,
            value=data["value"],
            # value=dtype(data["value"]),
            editable=bool(data["editable"]),
        )


class OperatorState(IntEnum):
    IDLE = auto()
    STARTED = auto()
    PAUSED = auto()
    STOPPED = auto()
    CRASHED = auto()


class Operator:
    """
    An operator subscribes to a source Observable, applies some
    transformations to the incoming items, and emits new/same items
    to subscribed operators.
    """

    def __init__(
            self,
            input_topics: Optional[Sequence[TopicName]] = None,
            output_topics: Optional[Sequence[TopicName]] = None,
            message_stream_type: str = "printer_stream",
            unique_id: Optional[str] = None,
            configurations: Optional[Dict[str, Any]] = None
    ):
        self.input_topics: Sequence[TopicName] = input_topics or []
        self.message_stream_type: str = message_stream_type
        self.message_stream: Optional[MessageStream] = None

        self.output_topics: Sequence[str] = output_topics or []
        """topics available in this operator instance to subscribe"""

        self.unique_id: str = unique_id or str(uuid.uuid4())

        self.configurations: Dict[str, Any] = configurations or dict()

        self.state: OperatorState = OperatorState.IDLE
        self._task: Optional[Task] = None
        """continues loop task which will be processing all the new messages as they come"""
        self._task_running_signal: asyncio.Event = asyncio.Event()
        """event is set until task is running"""

    @classmethod
    def from_function(
            cls,
            function: Callable,
            output_topics: Optional[Sequence[TopicName]] = None,
            input_topics: Optional[Sequence[TopicName]] = None,
            unique_id: Optional[str] = None,
            configurations: Optional[Dict[str, Any]] = None,
            **function_kwargs
    ):
        """method to generate Node from a json saved earlier"""

        instance = cls(
            input_topics=input_topics,
            output_topics=output_topics,
            unique_id=unique_id,
            configurations=configurations,
        )

        async def data_processor_function(self, data: Any, topic: str):
            return function(data, topic, **function_kwargs)

        instance.process_new_message = data_processor_function

        return instance

    def initialize(self):
        """handle initialization of message stream"""
        message_stream_parameters = self.configurations.get("message_stream_parameters", dict())
        self.message_stream = MESSAGE_STREAM_CATALOG[self.message_stream_type].load()(**message_stream_parameters)
        self.message_stream.initialize()
        self.message_stream.subscribe(topic=SYSTEM_COMMAND_TOPIC)
        self.message_stream.subscribe(topic=self.unique_id)
        for topic in self.input_topics:
            self.message_stream.subscribe(topic=topic)
        logger.info(f"Operator: {self.__class__.__name__}({self.unique_id}) initialized")

    async def pre_start(self):
        """to be called individually if the operator requires independent initialization"""
        logger.debug(f"Operator: {self.__class__.__name__}({self.unique_id}) starting")

    async def post_start(self):
        """to be called individually if the operator requires independent initialization"""
        pass

    async def pre_stop(self):
        """called before sending finalization notification to subscribers, should handle clearing up of this operator only"""
        pass

    async def post_stop(self):
        """called before sending finalization notification to subscribers, should handle clearing up of this operator only"""
        logger.debug(f"Operator: {self.__class__.__name__}({self.unique_id}) Stopped")

    async def pre_pause(self):
        """called before sending finalization notification to subscribers, should handle clearing up of this operator only"""
        pass

    async def post_pause(self):
        """called before sending finalization notification to subscribers, should handle clearing up of this operator only"""
        pass

    async def start(self):
        await self.pre_start()
        self.state = OperatorState.STARTED
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self.processor())
            self._task_running_signal.set()
        await self.post_start()
        await self._task

    async def processor(self):
        """to be called individually if the operator requires independent initialization"""
        while True:
            await self._task_running_signal.wait()
            topic, message = await self.message_stream.receive()
            if topic == SYSTEM_COMMAND_TOPIC:
                if message == SystemCommand.TERMINATE:
                    await self.finalize()
                elif message == SystemCommand.TERMINATE_ALL:
                    await self.finalize()
                    break
                elif message == SystemCommand.PAUSE:
                    await self.pause()
                elif message == SystemCommand.START:
                    await self.start()
                elif message == SystemCommand.STOP:
                    await self.stop()
            else:
                new_data = await self.process_new_message(data=message, topic=topic)

                # publish None response message only if allow_none_publish is true
                if new_data is not None and self.output_topics:
                    await self.publish(data=new_data, topic=self.output_topics[0])

    async def stop(self):
        """called before sending finalization notification to subscribers, should handle clearing up of this operator only"""
        await self.pre_stop()
        self._task_running_signal.clear()
        self.state = OperatorState.STOPPED
        await self.post_stop()

    async def pause(self):
        """called before sending finalization notification to subscribers, should handle clearing up of this operator only"""
        await self.pre_pause()
        self._task_running_signal.clear()
        self.state = OperatorState.PAUSED
        await self.post_pause()

    async def process_new_message(self, data: Any, topic: str) -> Any:
        """
        handle message from subscribers, whatever this function
        returns will be published to all the subscribers if not None.
        if required to publish for other topic do so in the function

        :param data: new data to be processed for respective topic
        :param topic: against which new data should be published
        """
        raise NotImplementedError()

    async def publish(self, data: Any, topic: str = None):
        """
        distribute data to subscribers if topic is default topic the data is distributed to all subscribers

        :param data: new data to be sent to respective subscribers
        :param topic: topic against which new data should be published
        :param force_await: if true, will await for all subscribers to process data, even if self.wait_for_subscribers is False
        """
        await self.message_stream.send(message=data, topic_name=topic or self.output_topics[0])

    async def finalize(self):
        """clear up all the work of this operator and notify the subscribers to finalize also"""
        await self.stop()
        # todo if required send a exit message to all

    def update_configuration(self, new_values: Dict[str, Any]):
        self.configurations.update(new_values)
        print(f"latest_configuration: {self.configurations}")

    def to_dict(self):
        """method to convert the node instance to json representation to be saved/shared"""
        return dict(
            object_type="operator",
            class_name=self.__class__.__name__,
            input_topics=self.input_topics,
            output_topics=self.output_topics,
            message_stream_type=self.message_stream_type,
            configurations=self.configurations,
            unique_id=self.unique_id,
            state=self.state.name
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """method to generate Node from a json saved earlier"""

        instance = cls(
            input_topics=data.get("input_topics"),
            output_topics=data.get("output_topics"),
            unique_id=data.get("unique_id"),
            message_stream_type=data.get("message_stream_type"),
            configurations=data.get("configurations"),
        )
        return instance
