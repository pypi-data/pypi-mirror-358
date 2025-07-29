from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict

__all__ = [
    "CheckpointMessage",
    "JobMessage",
    "ResultMessage",
    "LogMessage",
    "ModuleMessage",
    "SystemMessage",
    "ResultCheckpointMessage",
    "SerializationRequestMessage",
    "SerializationResultMessage",
]


class Message(BaseModel):
    model_config = ConfigDict(extra="allow")


class ModuleMessage(Message):
    id: str


class CheckpointMessage(Message):
    job_id: str
    checkpoint_id: int
    params: Dict[str, Any]


class ResultCheckpointMessage(Message):
    job_id: str
    checkpoint_id: int
    elapsed_time_seconds: Optional[int] = None


class JobMessage(Message):
    id: str
    job_type: str
    source_id: str
    params: Dict[str, Any]


class SerializationRequestMessage(Message):
    job_id: str
    job_type: str
    params: Dict[str, Any]
    output_format: str


class SerializationResultMessage(Message):
    job_id: str
    output_format: str


class ResultMessage(Message):
    job_id: str

    model_config = ConfigDict(extra="allow")


class LogMessage(Message):
    job_id: str
    message_type: str

    model_config = ConfigDict(extra="allow")


class SystemMessage(Message):
    pass
