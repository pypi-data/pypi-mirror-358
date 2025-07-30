import base64
import json
import typing as t
from typing import Any
from uuid import uuid4

import cloudpickle
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from ..enums import RunStatus
from . import ToolOutput

PICKLED_DATA_PREFIX = "__a79blob__"
PICKLED_DATA_PREFIX_DELIMITER = ":::"
PICKLED_DATA_SERIALIZATION_ERROR_MSG = "__serialization_error__"


class WorkflowCallbackHandler(BaseModel):
    """Simple callback protocol for workflow events."""

    # TODO: Add callbacks for workflow start, end, node start, end, error
    # if we need them in the external sdk


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


class NestedRunIdentifiers(BaseModel):
    """
    Identifies a specific workflow run within a potentially nested workflow hierarchy.

    For root/top-level workflow runs:
    - nested_run_id = str(run_id)  # String version of root run_id
    - parent_node_id = None
    - parent_run_id = None

    For nested workflow runs:
    - nested_run_id = "<uuid>"  # UUID string for nested runs
    - parent_node_id = "<node-id>"  # ID of node that triggered this nested workflow
    - parent_run_id = "<parent-run-id>"  # Parent's run identifier
    """

    # ID for this specific nested workflow run
    nested_run_id: str = Field(default_factory=lambda: str(uuid4()))

    # ID of the node that triggered this nested workflow (None for root runs)
    parent_node_id: str | None = None

    # Run ID of the parent workflow (None for root runs)
    parent_run_id: str | None = None


class RunnableConfig(BaseModel):
    """Configuration class for Runnable objects."""

    # Workflow id is used to identify the workflow definition
    workflow_id: str | None = None

    # Global id unique for the run of the workflow.
    root_run_id: str | None = None

    # Identifies this specific workflow run in the execution hierarchy
    run_identifiers: NestedRunIdentifiers = Field(
        default_factory=lambda: NestedRunIdentifiers()
    )

    artifacts_folder_id: int | None = None
    callbacks: list[WorkflowCallbackHandler] = []
    max_node_workers: int | None = None

    # Conversation ID for the workflow run
    # TODO: Will deprecate this in favor of a run_id. Workflow runs will be independent
    # of conversations. This will be removed in a future PR. Will add support for
    # run_id in a future PR.
    conversation_id: int | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("root_run_id", mode="before")
    @classmethod
    def convert_root_run_id_to_str(cls, v: Any) -> str | None:
        """Ensure root_run_id is always a string if provided.

        This handles backward compatibility for older runs
        """
        if isinstance(v, int):
            return str(v)
        # Allow None or existing strings
        if v is None or isinstance(v, str):
            return v
        # Raise error for other unexpected types
        raise ValueError("root_run_id must be a string or integer")
