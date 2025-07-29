from typing import Any

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.workflow_models import (
    RunnableResult,
    RunStatus,
    RunWorkflowInput,
    RunWorkflowOutput,
    ToolStreamResponse,
)

__all__ = [
    "RunStatus",
    "RunWorkflowInput",
    "RunWorkflowOutput",
    "RunnableResult",
    "ToolStreamResponse",
    "run_workflow",
]


def run_workflow(
    *,
    workflow_name: str,
    workflow_inputs: dict[str, Any],
    parent_run_id: str | None = DEFAULT,
    parent_node_id: str | None = DEFAULT,
) -> RunWorkflowOutput:
    """
    Run a workflow and wait for completion.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = RunWorkflowInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="workflow", name="run_workflow", input=input_model.model_dump()
    )
    return RunWorkflowOutput.model_validate(output_model)
