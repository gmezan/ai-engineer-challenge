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
        review_prompt = (
            "Decisión preliminar del sistema:\n"
            f"{json.dumps(decision, ensure_ascii=False)}\n\n"
            "Valida los detalles de la transacción y decide si se aprueba o se bloquea. "
            "Debes usar approve_transaction o reject_transaction para emitir la decisión final.\n"
            "IMPORTANTE: llama EXACTAMENTE una herramienta y no entregues decisión final en texto libre sin herramienta.\n"
            "Si no hay transaction_id disponible, usa transaction_id=\"UNKNOWN\"."
        )
        await ctx.send_message(review_prompt)
        await ctx.yield_output(review_prompt)
