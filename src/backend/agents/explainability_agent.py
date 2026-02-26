from typing import Any
from typing_extensions import Never

from agent_framework import Executor, WorkflowContext, handler


class ExplainabilityAgent(Executor):
    def __init__(self, id: str = "explainability"):
        super().__init__(id=id)

    @handler
    async def build_explainability(
        self,
        decision: dict[str, Any],
        ctx: WorkflowContext[Never, dict[str, Any]],
    ) -> None:
        output = decision
        await ctx.yield_output(output)
