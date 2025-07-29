from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterable, Dict, Generic, Type, TypeVar, Union, cast

from nerdd_module import Model
from nerdd_module.util import call_with_mappings
from stringcase import snakecase, spinalcase

from ..types import (
    CheckpointMessage,
    JobMessage,
    LogMessage,
    Message,
    ModuleMessage,
    ResultCheckpointMessage,
    ResultMessage,
    SerializationRequestMessage,
    SerializationResultMessage,
    SystemMessage,
)

__all__ = ["Channel", "Topic"]

T = TypeVar("T", bound=Message)


def get_job_type(job_type_or_model: Union[str, Model]) -> str:
    if isinstance(job_type_or_model, Model):
        model = job_type_or_model

        # create topic name from model name by
        # * converting to spinal case, (e.g. "MyModel" -> "my-model")
        # * converting to lowercase (just to be sure) and
        # * removing all characters except dash and alphanumeric characters
        # TODO: move to Module Id
        topic_name = spinalcase(model.name)
        topic_name = topic_name.lower()
        topic_name = "".join([c for c in topic_name if str.isalnum(c) or c == "-"])
        return topic_name
    else:
        return spinalcase(job_type_or_model)


class Topic(Generic[T]):
    def __init__(self, channel: Channel, name: str):
        self._channel = channel
        self._name = name

    async def receive(self, consumer_group: str) -> AsyncIterable[T]:
        async for msg in self.channel.iter_messages(self._name, consumer_group):
            yield cast(T, msg)

    async def send(self, message: T) -> None:
        await self.channel.send(self._name, message)

    @property
    def channel(self) -> Channel:
        return self._channel

    def __repr__(self) -> str:
        return f"Topic({self._name})"


class Channel(ABC):
    def __init__(self) -> None:
        self._is_running = False

    async def start(self) -> None:
        self._is_running = True
        await self._start()

    async def _start(self) -> None:  # noqa: B027
        pass

    async def stop(self) -> None:
        await self._stop()
        self._is_running = False

    async def _stop(self) -> None:  # noqa: B027
        pass

    async def __aenter__(self) -> Channel:
        await self.start()
        return self

    async def __aexit__(self, exc_type: type, exc_value: Exception, traceback: object) -> None:
        await self.stop()

    #
    # RECEIVE
    #
    async def iter_messages(self, topic: str, consumer_group: str) -> AsyncIterable[Message]:
        if not self._is_running:
            raise RuntimeError("Channel is not running. Call start() first.")
        async for message in self._iter_messages(topic, consumer_group):
            yield message

    # Insane glitch: we need to use "def _iter_messages" instead of "async def _iter_messages"
    # here, because the method doesn't use "yield" and so the type checker will assume that the
    # actual type is Coroutine[AsyncIterable[Message], None, None].
    @abstractmethod
    def _iter_messages(self, topic: str, consumer_group: str) -> AsyncIterable[Message]:
        pass

    #
    # SEND
    #
    async def send(self, topic: str, message: Message) -> None:
        if not self._is_running:
            raise RuntimeError("Channel is not running. Call start() first.")
        await self._send(topic, message)

    @abstractmethod
    async def _send(self, topic: str, message: Message) -> None:
        pass

    #
    # TOPICS
    #
    def modules_topic(self) -> Topic[ModuleMessage]:
        return Topic[ModuleMessage](self, "modules")

    def jobs_topic(self) -> Topic[JobMessage]:
        return Topic[JobMessage](self, "jobs")

    def checkpoints_topic(self, job_type_or_model: Union[str, Model]) -> Topic[CheckpointMessage]:
        job_type = get_job_type(job_type_or_model)
        topic_name = f"{job_type}-checkpoints"
        return Topic[CheckpointMessage](self, topic_name)

    def results_topic(self) -> Topic[ResultMessage]:
        return Topic[ResultMessage](self, "results")

    def result_checkpoints_topic(self) -> Topic[ResultCheckpointMessage]:
        return Topic[ResultCheckpointMessage](self, "result-checkpoints")

    def serialization_requests_topic(self) -> Topic[SerializationRequestMessage]:
        return Topic[SerializationRequestMessage](self, "serialization-requests")

    def serialization_results_topic(self) -> Topic[SerializationResultMessage]:
        return Topic[SerializationResultMessage](self, "serialization-results")

    def logs_topic(self) -> Topic[LogMessage]:
        return Topic[LogMessage](self, "logs")

    def system_topic(self) -> Topic[SystemMessage]:
        return Topic[SystemMessage](self, "system")

    #
    # META
    #
    _channel_registry: Dict[str, Type["Channel"]] = {}

    @classmethod
    def __init_subclass__(
        cls,
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)

        # check if class ends with "Channel"
        if cls.__name__.endswith("Channel"):
            name = cls.__name__[: -len("Channel")]
            name = snakecase(name)
        else:
            name = cls.__name__

        # register the channel class
        Channel._channel_registry[name] = cls

    @classmethod
    def get_channel(cls, name: str) -> Channel:
        return cls._channel_registry[name]()

    @classmethod
    def create_channel(cls, name: str, **kwargs: Any) -> Channel:
        return call_with_mappings(cls._channel_registry[name], kwargs)

    @classmethod
    def get_channel_names(cls) -> list[str]:
        return list(cls._channel_registry.keys())
