import base64
import json
import typing as t

import cloudpickle
from pydantic import BaseModel, Field, field_serializer, field_validator

from ..enums import RunStatus
from . import ToolOutput

PICKLED_DATA_PREFIX = "__a79blob__"
PICKLED_DATA_PREFIX_DELIMITER = ":::"
PICKLED_DATA_SERIALIZATION_ERROR_MSG = "__serialization_error__"


class RunWorkflowInput(BaseModel):
    """Input data model for workflow runner."""

    workflow_name: str = Field(description="Name of the workflow to run")
    workflow_inputs: dict[str, t.Any] = Field(
        description="Optional input data to pass to the workflow"
    )
    parent_run_id: str | None = None
    parent_node_id: str | None = None


class RunWorkflowOutput(ToolOutput):
    content: dict[str, t.Any] = Field(description="Output of the workflow")


StreamId = t.NewType("StreamId", str)


class ToolStreamResponse(BaseModel):
    stream_id: StreamId
    tool_name: t.Optional[str]
    package_name: t.Optional[str]


class RunnableResult(BaseModel):
    """
    Dataclass representing the result of a Runnable execution.

    Attributes:
        status (RunStatus): The status of the execution.
        input (Any): The input data of the execution.
        output (Any): The output data of the execution.
    """

    status: RunStatus
    input: t.Any = None
    output: t.Any = None
    error_msg: str = ""
    # Note: Simplified version without UserActionType dependency for now
    user_action_type: str = "none"

    @field_serializer("input", "output")
    def serialize_input_output(self, value: t.Any) -> t.Any:
        def _encode(val: t.Any) -> t.Any:
            if isinstance(val, dict):
                return {k: _encode(v) for k, v in val.items()}

            if isinstance(val, (list, tuple)):
                return [_encode(v) for v in val]

            try:
                json.dumps(val)
                return val
            except (TypeError, OverflowError):
                try:
                    encoded = base64.b64encode(cloudpickle.dumps(val)).decode("utf-8")
                    return (
                        f"{PICKLED_DATA_PREFIX}{PICKLED_DATA_PREFIX_DELIMITER}"
                        f"{type(val).__name__}{PICKLED_DATA_PREFIX_DELIMITER}{encoded}"
                    )
                except Exception:
                    return (
                        f"{PICKLED_DATA_PREFIX}{PICKLED_DATA_PREFIX_DELIMITER}"
                        f"{type(val).__name__}{PICKLED_DATA_PREFIX_DELIMITER}"
                        f"{PICKLED_DATA_SERIALIZATION_ERROR_MSG}"
                    )

        return _encode(value)

    @staticmethod
    def _decode_pickled(val: t.Any) -> t.Any:
        """Decode pickled values that were serialized by ``serialize_input_output``.

        This reverses the logic used during serialization by detecting the
        ``__a79blob__`` prefix and unpickling the base-64 encoded payload.
        """

        if isinstance(val, str) and val.startswith(PICKLED_DATA_PREFIX):
            try:
                _, type_name, encoded = val.split(PICKLED_DATA_PREFIX_DELIMITER, 2)
            except ValueError:
                return val

            if encoded == PICKLED_DATA_SERIALIZATION_ERROR_MSG or not encoded:
                return f"<{type_name}>"

            try:
                return cloudpickle.loads(base64.b64decode(encoded))
            except Exception:
                return f"<{type_name}>"

        if isinstance(val, dict):
            return {k: RunnableResult._decode_pickled(v) for k, v in val.items()}

        if isinstance(val, list):
            return [RunnableResult._decode_pickled(v) for v in val]

        if isinstance(val, tuple):
            return tuple(RunnableResult._decode_pickled(v) for v in val)

        return val

    @field_validator("input", "output", mode="before")
    @classmethod
    def decode_input_output(cls, v: t.Any) -> t.Any:
        """Decode any pickled blobs present in the input/output fields."""
        return cls._decode_pickled(v)
