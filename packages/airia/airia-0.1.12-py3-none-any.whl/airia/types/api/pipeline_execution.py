from typing import Any, AsyncIterator, Dict, Iterator

from pydantic import BaseModel, ConfigDict, Field

from ..sse import SSEMessage


class PipelineExecutionResponse(BaseModel):
    result: str
    report: None
    is_backup_pipeline: bool = Field(alias="isBackupPipeline")


class PipelineExecutionDebugResponse(BaseModel):
    result: str
    report: Dict[str, Any]
    is_backup_pipeline: bool = Field(alias="isBackupPipeline")


class PipelineExecutionStreamedResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    stream: Iterator[SSEMessage]


class PipelineExecutionAsyncStreamedResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    stream: AsyncIterator[SSEMessage]
