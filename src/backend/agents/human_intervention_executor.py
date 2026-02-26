import logging
from typing import Annotated

from agent_framework import AgentExecutor, tool
from agent_framework.azure import AzureOpenAIChatClient
from pydantic import Field


logger = logging.getLogger(__name__)


@tool(approval_mode="always_require", name="approve_transaction")
def approve_transaction(
    transaction_id: Annotated[
        str,
        Field(description="Transaction ID to verify. If unavailable, use 'UNKNOWN'."),
    ] = "UNKNOWN",
) -> str:
    """Approve a transaction."""
    logger.info("[HUMAN_REVIEW] approve_transaction called with transaction_id=%s", transaction_id)
    return f"Transaction {transaction_id} has been APPROVED by human review."


@tool(approval_mode="always_require", name="reject_transaction")
def reject_transaction(
    transaction_id: Annotated[
        str,
        Field(description="Transaction ID to verify. If unavailable, use 'UNKNOWN'."),
    ] = "UNKNOWN",
) -> str:
    """Reject a transaction."""
    logger.info("[HUMAN_REVIEW] reject_transaction called with transaction_id=%s", transaction_id)
    return f"Transaction {transaction_id} has been BLOCKED by human review."


class HumanInterventionExecutor(AgentExecutor):
    INSTRUCTIONS = """
Eres un analista de fraude que participa en un debate técnico balanceado. Tu función es aprobar o rechazar transacciones
Recibirás evidencia de una transacción y la decisión preliminar tomada por el sistema de análisis automatizado.
Siempre confirma los detalles antes de realizar una aprobación o rechazo.
Debes usar approve_transaction o reject_transaction para emitir la decisión final.

Reglas de uso de herramientas (obligatorias):
- Debes llamar EXACTAMENTE una herramienta: approve_transaction o reject_transaction.
- No emitas la decisión final en texto libre sin llamar herramienta.
- Si no encuentras transaction_id, llama la herramienta con transaction_id="UNKNOWN".
- Tras ejecutar la herramienta, entrega un mensaje breve de confirmación.
"""

    def __init__(self, client: AzureOpenAIChatClient, name: str = "human_intervention_agent"):
        agent = client.as_agent(
            name=name,
            instructions=self.INSTRUCTIONS,
            tools=[approve_transaction, reject_transaction],
        )
        super().__init__(agent=agent, id=name)

