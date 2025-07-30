import copy
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Self, Set, Tuple, TypeVar

from sortedcontainers import SortedDict, SortedList

from nqs_sdk.shared_kernel import (
    MessageDispatcherMessageTryToTimeTravelError,
    MessageDispatcherUnRegistredProducerError,
    MessageDispatcherValidationError,
)
from nqs_sdk.shared_kernel.pickable_generator import PickableGenerator, StatefulGenerator


class ID:
    def __init__(self, id_value: str):
        self.value = id_value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ID):
            raise NotImplementedError
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, ID):
            raise NotImplementedError
        return self.value < other.value


class Message(ABC):
    def __init__(self, time_index: int = 0):
        self._time_index = time_index

    def time_index(self) -> int:
        return self._time_index

    def name(self) -> str:
        return self.__class__.__name__

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Message):
            raise NotImplementedError
        return self.time_index() < other.time_index()


class ObserveCall(Message):
    protocol_id: ID | None = None

    def __init__(self, block_number: int, protocol_id: ID | None = None) -> None:
        super().__init__(block_number)
        self.protocol_id = protocol_id

    def time_index(self) -> int:
        return self._time_index

    def __str__(self) -> str:
        return f"ObserveCall(block_number={self._time_index}, protocol_id={self.protocol_id})"


M = TypeVar("M", bound=Message)


class MessageProducer(ABC):
    def __init__(self, name: str) -> None:
        self._producer_id: ID = ID(name)
        self._message_dispatcher: MessageDispatcher

    def get_producer_id(self) -> ID:
        return self._producer_id

    @abstractmethod
    def produce_next_message(self, **kwargs: Any) -> PickableGenerator:
        pass


class MessageListener(ABC, Generic[M]):
    @abstractmethod
    def handle(self, message: M) -> None:
        pass


class MessageDispatcher(ABC):
    @abstractmethod
    def post(self, producer_id: ID, topic: str, message: Message) -> None:
        pass

    @abstractmethod
    def direct_post(self, producer_id: ID, topic: str, message: Message) -> None:
        pass

    @abstractmethod
    def register_producer(self, producer: MessageProducer, topic: str) -> ID:
        pass

    @abstractmethod
    def register_listener(self, message_class: type, listener: MessageListener, topic: str = "DEFAULT") -> Self:
        pass

    @abstractmethod
    def count_remaining_message_for_time_index(self, time_index: int, topic: str = "DEFAULT") -> int:
        pass

    @abstractmethod
    def start(self, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def start_pulling(self, low_time_index: int, high_time_index: int, topic: str = "DEFAULT") -> None:
        pass


class ObserverMessageProducer(MessageProducer):
    def __init__(self, block_grid: List[int], message_dispatcher: MessageDispatcher, topic: str = "DEFAULT") -> None:
        super().__init__("zzzzObserverMessageProducer")
        self._block_grid = block_grid
        self._message_dispatcher = message_dispatcher
        self.topic = topic

    def produce_next_message(self, **kwargs: Any) -> PickableGenerator:
        def update(state: Tuple[int, List[int]]) -> Tuple[Tuple[int, List[int]], None]:
            i, calls = state
            if i >= len(calls):
                raise StopIteration
            self._message_dispatcher.post(self._producer_id, self.topic, ObserveCall(calls[i], self._producer_id))
            return ((i + 1, calls), None)

        return StatefulGenerator((0, self._block_grid), update)


class DefaultMessageDispatcher(MessageDispatcher):
    def __init__(
        self,
        block_grid: List[int],
        low_watermark: int = -1,
    ):
        # The broker initializes the observers on the first block so we can skip it here
        self._block_grid = copy.deepcopy(block_grid[1:])
        self._listeners: Dict[Tuple[type, str], List[MessageListener]] = {}
        self._registry_producers: Dict[ID, MessageProducer] = SortedDict({})
        self._registered_ids: Dict[str, List[ID]] = SortedDict({})
        self._producers: Dict[ID, PickableGenerator] = {}
        self._exhausted_producers: Dict[ID, bool] = {}
        self._message_buffer: Dict[str, Dict[ID, List[Message]]] = {}
        self.time_index_buffer: Dict[str, Dict[ID, int]] = {}
        self._low_watermark: int = low_watermark
        self._number_of_message_in_process: int = 0
        self._is_started = False

    def start(self, **kwargs: Any) -> None:
        low_watermark = kwargs.get("low_watermark", -1)
        if self._is_started is True:
            raise RuntimeError("Start MessageDispatcher when it's already started")
        self._is_started = True
        self._low_watermark = low_watermark

    def register_producer(self, producer: MessageProducer, topic: str) -> ID:
        producer_id = producer.get_producer_id()
        if topic not in self._registered_ids:
            self._registered_ids[topic] = []
        if producer_id not in self._registered_ids[topic]:
            self._registered_ids[topic].append(producer_id)
        self._registry_producers[producer_id] = producer
        return producer_id

    def register_listener(self, message_class: type, listener: MessageListener, topic: str = "DEFAULT") -> Self:
        key = (message_class, topic)
        self._listeners.setdefault(key, []).append(listener)
        return self

    def direct_post(self, producer_id: ID, topic: str, message: Message) -> None:
        self._check_registration(producer_id)
        message_type = type(message)
        compatible_listeners = self._get_compatible_listeners(message_type, topic)

        if not compatible_listeners:
            raise MessageDispatcherValidationError(f"Can't execute {message.name()} no compatible listeners")

        for listener in compatible_listeners:
            listener.handle(message)

    def post(self, producer_id: ID, topic: str, message: Message) -> None:
        self._check_registration(producer_id)
        self._check_time_index(message)

        self._update_message_buffer(producer_id, topic, message)

    def count_remaining_message_for_time_index(self, time_index: int, topic: str = "DEFAULT") -> int:
        if topic not in self._message_buffer:
            return 0

        topic_buffer = self._message_buffer[topic]
        count = 0
        for messages in topic_buffer.values():
            for message in messages:
                if message.time_index() == time_index:
                    count += 1
        return count + max(self._number_of_message_in_process - 1, 0)

    def _update_message_buffer(self, producer_id: ID, topic: str, message: Message) -> None:
        self._message_buffer.setdefault(topic, {}).setdefault(producer_id, []).append(message)
        self.time_index_buffer.setdefault(topic, {})[producer_id] = message.time_index()

    def start_pulling(self, low_time_index: int, high_time_index: int, topic: str = "DEFAULT") -> None:
        self._initialize_producers(low_time_index, high_time_index, topic)
        self._pull_and_dispatch_messages(topic)

    def _initialize_producers(self, low_time_index: int, high_time_index: int, topic: str) -> None:
        observation_producer = ObserverMessageProducer(self._block_grid, self, topic)
        self.register_producer(observation_producer, topic)
        self._producers = SortedDict(
            {
                producer_id: producer.produce_next_message(
                    block_number_from=low_time_index + 1, block_number_to=high_time_index
                )
                for producer_id, producer in self._registry_producers.items()
            }
        )

        self._exhausted_producers = {producer_id: False for producer_id in self._producers}

    def _pull_and_dispatch_messages(self, topic: str) -> None:
        while not all(self._exhausted_producers.values()) or not self._message_buffer_is_empty(topic):
            producers_to_query = self._get_producers_to_query(topic)
            if len(producers_to_query) != 0:
                self._pull_messages_from_producers(producers_to_query)
            if not self._handle_message_dispatcher_and_time_update(topic):
                break

    def _message_buffer_is_empty(self, topic: str) -> bool:
        for message_list in self._message_buffer.get(topic, {}).values():
            if message_list:
                return False
        return True

    def _get_producers_to_query(self, topic: str) -> Set[ID]:
        registered_producers = set(self._registered_ids.get(topic, []))
        exhausted_producers = {
            producer_id for producer_id, is_exhausted in self._exhausted_producers.items() if is_exhausted
        }
        producers_with_messages = {
            producer_id for producer_id, messages in self._message_buffer.get(topic, {}).items() if messages
        }
        return registered_producers - exhausted_producers - producers_with_messages

    def _handle_message_dispatcher_and_time_update(self, topic: str) -> bool:
        if topic not in self.time_index_buffer:
            return False

        current_time_index = self._get_next_time_index(topic)
        if current_time_index is None:
            return False

        while True:
            dispatched = self._dispatch_messages_at_time_index(topic, current_time_index)
            if not dispatched:
                break

        self._update_low_watermark(current_time_index, topic)
        return True

    def _dispatch_messages_at_time_index(self, topic: str, time_index: int) -> bool:
        producers_to_dispatch = self._get_producers_to_dispatch(topic, time_index)
        for producer_id in producers_to_dispatch:
            self._dispatch_messages(topic, producer_id)
        return len(producers_to_dispatch) != 0

    def _get_producers_to_dispatch(self, topic: str, time_index: int) -> SortedList:
        return SortedList(
            [
                producer_id
                for producer_id, msg_time_index in self.time_index_buffer[topic].items()
                if msg_time_index == time_index
            ]
        )

    def _dispatch_messages(self, topic: str, producer_id: ID) -> None:
        messages = self._message_buffer[topic][producer_id].copy()
        self._clear_buffers_for_producer(topic, producer_id)
        self._pull_messages_from_producers({producer_id})
        self._number_of_message_in_process = len(messages)
        for message in messages:
            self._check_time_index(message)
            message_type = type(message)
            compatible_listeners = self._get_compatible_listeners(message_type, topic)

            if not compatible_listeners:
                raise MessageDispatcherValidationError(f"Can't execute {message.name()} no compatible listeners")

            for listener in compatible_listeners:
                listener.handle(message)

    def _clear_buffers_for_producer(self, topic: str, producer_id: ID) -> None:
        del self._message_buffer[topic][producer_id]
        del self.time_index_buffer[topic][producer_id]

    def _get_compatible_listeners(self, message_type: type, topic: str) -> List[MessageListener]:
        return [
            listener
            for (msg_class, candidate_topic), listeners in self._listeners.items()
            if candidate_topic == topic and issubclass(message_type, msg_class)
            for listener in listeners
        ]

    def _get_next_time_index(self, topic: str) -> Optional[int]:
        if topic in self.time_index_buffer and self.time_index_buffer[topic]:
            return min(self.time_index_buffer[topic].values())
        return None

    def _update_low_watermark(self, current_time_index: int, topic: str) -> None:
        next_time_index = self._get_next_time_index(topic)
        if next_time_index is None or self._low_watermark != next_time_index:
            self._low_watermark = current_time_index

    def _pull_messages_from_producers(self, producers_to_query: Set[ID]) -> None:
        for producer_id in producers_to_query:
            try:
                next(self._producers[producer_id])
            except StopIteration:
                self._exhausted_producers[producer_id] = True

    def _check_registration(self, producer_id: ID) -> None:
        if producer_id not in self._registry_producers:
            raise MessageDispatcherUnRegistredProducerError(
                f"An unregistered producer tried to publish values {producer_id}"
            )

    def _check_time_index(self, message: Message) -> None:
        if message.time_index() < self._low_watermark:
            raise MessageDispatcherMessageTryToTimeTravelError(
                f"message from the past attempt to time travel, {message}, "
                + f"current time index: {self._low_watermark}"
            )
