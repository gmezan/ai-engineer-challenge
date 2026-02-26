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
        Field(description="Transaction ID to verify. If unavailable, use 'UNKNOWN'."),
    ] = "UNKNOWN",
) -> str:
    logger.info(
        "[EXPLAINABILITY_HUMAN_REVIEW] review_transaction called with transaction_id=%s",
        transaction_id,
    )
    return f"Transaction {transaction_id} has been APPROVED by human review."


class ExplainabilityAgent(AgentExecutor):
    INSTRUCTIONS = dedent(
        """
        Eres el agente de explicabilidad final.

        Recibirás la decisión del árbitro como JSON.
        - Si decision == "ESCALATE_TO_HUMAN": debes llamar EXACTAMENTE una vez la herramienta review_transaction.
        - Si decision es distinta de "ESCALATE_TO_HUMAN": NO debes llamar herramientas.

        Responde con un JSON válido que preserve la decisión y agregue explicación final breve.
        """.strip()
    )

    def __init__(self, client: AzureOpenAIChatClient, name: str = "explainability"):
        agent = client.as_agent(
            name=name,
            instructions=self.INSTRUCTIONS,
            tools=[review_transaction],
        )
        super().__init__(agent=agent, id=name)
