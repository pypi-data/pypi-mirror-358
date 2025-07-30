import uuid
from typing import Protocol, Dict, Any, List, Optional, Sequence

from loguru import logger

from pydhara import TopicName, OperatorID, SubscriptionID, OPERATOR_CATALOG

class Pipeline(Protocol):
    """
    [ ] handle subscription and topics
    [ ] provide api/method for subscription and removal of subscription
    [x] it could also handle execution of operators, while registering the operator to backend we can define its lifecycle, thread/process, resources and other details
    [x] it should initialize the operator instances based on requirement
    [x] Pipeline API - where we will be giving operator class to the backend and backend will handle its initialization and lifecycle
    [x] provides custom stream abstractions to the operators for reading and writing serialized messages
    """
    topic_registry: Dict[str, Any]
    """record of available topics and their information"""

    operator_configs: Dict[str, Dict[str, Any]]
    """initialization configurations of operators for the pipeline"""

    @property
    def available_topics(self) -> List[TopicName]:
        pass

    # async def publish(self, message: Any, topic: TopicName = DEFAULT_TOPIC):
    #     """send the message to the specified topic"""
    #     pass

    def add_new_operator(
            self,
            operator_name: str,
            output_topics: Optional[Sequence[TopicName]] = None,
            input_topics: Optional[Sequence[TopicName]] = None,
            operator_kwargs: Optional[Dict[str, Any]] = None,
            start_in_subprocess: bool = False
    ) -> Optional[OperatorID]:
        """
        Define operator configurations and add it to registry and add subscriptions
        based on the topics to expect from operator.

        :param operator_name: operator class name matching with catalog to initialize
        :param input_topics: list of topics to which this operator will be listening for
        :param output_topics: list of topics to which this operator can send messages
        :param operator_kwargs: parameters to be passed for operator initialization
        :param start_in_subprocess: if true operator will be initialized in separate process
        :return: initialized operator id or None if operator not found with same name
        """
        if operator_name not in OPERATOR_CATALOG.names:
            logger.error(f"No Implementation found for Operator with name: {operator_name}")
            return None

        operator_kwargs = operator_kwargs or dict()
        unique_id = str(uuid.uuid4())
        self.operator_configs[unique_id] = dict(
            operator_name=operator_name,
            input_topics=input_topics,
            output_topics=output_topics,
            start_in_subprocess=start_in_subprocess,
            unique_id=unique_id,
            **operator_kwargs
        )
        return unique_id

    async def remove_operator(self, operator_id: OperatorID) -> bool:
        pass

    async def add_subscription(self, topic: TopicName, operator_id: OperatorID) -> SubscriptionID:
        pass

    async def remove_subscription_by_id(self, subscription_id: SubscriptionID):
        pass

    async def remove_subscription_by_operator_id(self, topic: TopicName, operator_id: OperatorID):
        pass

    def to_dict(self) -> Dict[str, Any]:
        pass

    @classmethod
    async def from_dict(cls, data: Dict[str, Any]) -> "Pipeline":
        pass

    async def start(self) -> bool:
        """start all the operators"""
        pass

    async def stop(self) -> bool:
        """stop all the operators"""
        pass

    async def pause(self) -> bool:
        """pause all the operators"""
        pass

    async def dispose(self) -> bool:
        """dispose all the operators and topic streams"""
        pass
