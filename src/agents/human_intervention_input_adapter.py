import json
from typing import Any

from agent_framework import Executor, WorkflowContext, handler


class HumanInterventionInputAdapter(Executor):
    def __init__(self, id: str = "human_intervention_input_adapter"):
        super().__init__(id=id)

    @handler
    async def adapt(
        self,
        decision: dict[str, Any],
        ctx: WorkflowContext[str, str],
    ) -> None:
        review_prompt = ("Review transaction")
        await ctx.yield_output(review_prompt)
        await ctx.send_message(review_prompt)
