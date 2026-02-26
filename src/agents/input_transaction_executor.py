import json
from typing import Annotated

from agent_framework import (
    AgentExecutor,
    tool,
)
from agent_framework.azure import AzureOpenAIChatClient
from pydantic import BaseModel

from data.cosmos_connection import CHALLENGE_DATABASE_NAME, close_cosmos_client, get_cosmos_database_client


TRANSACTIONS_CONTAINER = "transactions"


class TransactionLookupOutput(BaseModel):
    transaction: str


def _strip_system_fields(value):
    if isinstance(value, dict):
        return {k: _strip_system_fields(v) for k, v in value.items() if not k.startswith("_")}
    if isinstance(value, list):
        return [_strip_system_fields(item) for item in value]
    return value


@tool
def search_transaction_by_id(
    transaction_id: Annotated[str, "Transaction ID to query in transactions container"],
) -> str:
    """Search the transactions container in Cosmos DB by transaction_id."""
    try:
        client, database = get_cosmos_database_client()
        container = database.get_container_client(TRANSACTIONS_CONTAINER)
        query = "SELECT * FROM c WHERE c.transaction_id = @transaction_id"
        parameters = [{"name": "@transaction_id", "value": transaction_id}]
        items = list(
            container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
            )
        )

        if not items:
            return f"No transaction found for transaction_id={transaction_id}."

        sanitized = _strip_system_fields(items[0])
        return json.dumps(sanitized, ensure_ascii=False, default=str)
    except Exception as exc:
        return (
            f"Error querying {CHALLENGE_DATABASE_NAME}.{TRANSACTIONS_CONTAINER} "
            f"for transaction_id={transaction_id}: {exc}"
        )
    finally:
        if "client" in locals():
            close_cosmos_client(client)


class InputTransactionExecutor(AgentExecutor):
    INSTRUCTIONS = """
Eres un analista de transacciones.
Extrae transaction_id del mensaje de entrada y usa la herramienta search_transaction_by_id.
Responde en formato JSON estricto con la forma {"transaction": "..."}.
El campo transaction debe contener exactamente el resultado completo de la herramienta, sin resumir ni añadir texto adicional.
"""

    def __init__(self, client: AzureOpenAIChatClient, name: str = "input_transaction_executor"):
        agent = client.as_agent(
            name=name,
            instructions=self.INSTRUCTIONS,
            tools=[search_transaction_by_id],
            default_options={"response_format": TransactionLookupOutput},
        )
        super().__init__(agent=agent, id=name)