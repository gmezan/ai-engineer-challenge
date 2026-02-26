from __future__ import annotations

import logging
from textwrap import dedent
from typing import Annotated

from agent_framework import ChatAgent, ChatClientProtocol, ai_function
from agent_framework_ag_ui import AgentFrameworkAgent
from pydantic import Field

logger = logging.getLogger(__name__)


@ai_function(
    approval_mode="always_require",
    name="review_transaction",
    description="Approve a transaction.",
)
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


def create_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    """Instantiate the CopilotKit transaction approver agent."""
    base_agent = ChatAgent(
        name="human_intervention_agent",
        instructions=dedent(
            """
            Eres un analista de fraude que procesa transacciones por su id.
            
            Reglas de uso de herramientas (obligatorias):
            - Debes llamar EXACTAMENTE una herramienta: review_transaction.
            """.strip()
        ),
        chat_client=chat_client,
        tools=[review_transaction],
    )

    return AgentFrameworkAgent(
        agent=base_agent,
        name="CopilotKitMicrosoftAgentFrameworkAgent",
        description="Handles human-reviewed transaction approvals and rejections.",
        require_confirmation=False,
    )
