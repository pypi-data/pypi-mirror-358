import asyncio
from multiprocessing import Process
from threading import Thread
from typing import Dict, Any, Optional, List, Union

from loguru import logger
import zmq
from zmq.asyncio import Context

from pydhara import SystemCommand, TopicName, OperatorID, SubscriptionID, SYSTEM_COMMAND_TOPIC, OPERATOR_CATALOG
from pydhara.core.message_stream import MessageStream
from pydhara.core.pipeline import Pipeline
from pydhara.zmq.message_stream import ZMQBasicReaderWriterMessageStream, DEFAULT_READER_URL, DEFAULT_WRITER_URL


class ZMQCentralPipeline(Pipeline):
    def __init__(self, writer_endpoint: str = DEFAULT_WRITER_URL, reader_endpoint: str = DEFAULT_READER_URL):
        self.writer_endpoint = writer_endpoint
        self.reader_endpoint = reader_endpoint
        self.topic_registry = dict()
        self.operator_configs = dict()

        self._proxy_process = None
        self._system_message_stream: Optional[MessageStream] = None
        self._processes = dict()

    @staticmethod
    def proxy(writer_url, reader_url):
        ctx = Context()
        in_s = ctx.socket(zmq.XSUB)
        in_s.bind(writer_url)

        out_s = ctx.socket(zmq.XPUB)
        out_s.bind(reader_url)

        try:
            logger.debug("proxy started")
            zmq.proxy(in_s, out_s)
            logger.debug("proxy ended")
        except zmq.ContextTerminated:
            logger.debug("proxy terminated")
            in_s.close()
            out_s.close()

    @property
    def available_topics(self) -> List[TopicName]:
        return list(self.topic_registry.keys())

    async def remove_operator(self, operator_id: OperatorID) -> bool:
        op = self.operator_configs.get(operator_id, None)
        if op is None:
            logger.warning(f"Error Removing Operator: no operator found with id - {operator_id}")
            return False
        else:
            self.operator_configs.pop(operator_id)
            return True

    async def add_subscription(self, topic: TopicName, operator_id: OperatorID) -> SubscriptionID:
        pass

    async def remove_subscription_by_id(self, subscription_id: SubscriptionID):
        pass

    async def remove_subscription_by_operator_id(self, topic: TopicName, operator_id: OperatorID):
        pass

    def to_dict(self) -> Dict[str, Any]:
        pass

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZMQCentralPipeline":
        pass

    def initialize(self):
        """allocate and connect all the memory data and streams for all operators"""
        self._proxy_process = Process(target=self.proxy, args=(self.writer_endpoint, self.reader_endpoint), daemon=True)
        self._proxy_process.start()

        self._system_message_stream = ZMQBasicReaderWriterMessageStream()
        self._system_message_stream.initialize()

        self._processes: Dict[str, Union[Process, Thread]] = dict()

        for operator_cfg in self.operator_configs.values():
            if operator_cfg.get("run_in_subprocess", True):
                print("starting in subprocess")
                task = Process(target=self.operator_runner, args=(operator_cfg,), daemon=True)
            else:
                task = Thread(target=self.operator_runner, args=(operator_cfg,), daemon=True)
            task.start()
            self._processes[operator_cfg["unique_id"]] = task

        return True

    @staticmethod
    def operator_runner(config: Any):
        """
        initialize the operator and add it to registry and add subscriptions
        based on the topics to expect from operator add the operator port to
        respective topic id in topic_registry
        """

        async def runner():
            logger.info(f"trying to run operator with cfg: {config}")
            operator_type = OPERATOR_CATALOG[config["operator_name"]]
            operator = operator_type.from_dict(dict(**config, message_stream_type="ZMQBasicReaderWriterMessageStream"))
            logger.info("trying to initialize operator")
            operator.initialize()
            logger.info("trying to start operator")
            await operator.start()

        asyncio.run(runner())

    async def start(self) -> bool:
        """start all the operators"""
        if self._proxy_process is None:
            logger.error("Failed to start, Pipeline not Initialized")

        await self._system_message_stream.send(topic_name=SYSTEM_COMMAND_TOPIC, message=SystemCommand.START.value)

        terminate_pipeline = False

        while len(self._processes) > 0:
            if terminate_pipeline:
                await self._system_message_stream.send(topic_name=SYSTEM_COMMAND_TOPIC, message=SystemCommand.TERMINATE_ALL)

            for key in list(self._processes.keys()):
                task = self._processes[key]
                if not task.is_alive():
                    if task.exitcode > 0:
                        logger.critical("One of the Operator crashed, requesting all operators to terminate")
                        await self._system_message_stream.send(topic_name=SYSTEM_COMMAND_TOPIC, message=SystemCommand.TERMINATE_ALL)
                        terminate_pipeline = True
                    self._processes.pop(key)
            await asyncio.sleep(1)

        self._proxy_process.terminate()
        return True
