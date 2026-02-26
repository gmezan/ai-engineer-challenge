from __future__ import annotations

import logging
from textwrap import dedent
from typing import Annotated

from agent_framework import AgentExecutor, tool
from agent_framework.azure import AzureOpenAIChatClient
from pydantic import Field

logger = logging.getLogger(__name__)


@tool(approval_mode="always_require", name="review_transaction")
def review_transaction(
    transaction_id: Annotated[
        str,
        Field(
            description="Transaction ID to verify. If unavailable, use 'UNKNOWN'."
        ),
    ] = "UNKNOWN",
) -> str:
    """Approve a transaction."""
    logger.info(
        "[HUMAN_REVIEW] review_transaction called with transaction_id=%s",
        transaction_id,
    )
    return f"Transaction {transaction_id} has been APPROVED by human review."


def get_base_agent(chat_client: AzureOpenAIChatClient):
    """Instantiate the human intervention base agent."""
    return chat_client.as_agent(
        name="human_intervention_agent",
        instructions=dedent(
            """
            Eres un analista de fraude que procesa transacciones por su id.
            
            Reglas de uso de herramientas (obligatorias):
            - Debes llamar EXACTAMENTE una herramienta: review_transaction.
            """.strip()
        ),
        tools=[review_transaction],
    )


def create_agent(chat_client: AzureOpenAIChatClient):
    """Backward-compatible factory for existing integrations."""
    return get_base_agent(chat_client)


class HumanInterventionExecutor(AgentExecutor):
    def __init__(
        self,
        client: AzureOpenAIChatClient,
        name: str = "HumanInterventionExecutor",
    ):
        super().__init__(agent=get_base_agent(client), id=name)
