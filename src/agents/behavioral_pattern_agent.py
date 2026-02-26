import json
from typing import Annotated

from agent_framework import AgentExecutor, tool
from agent_framework.azure import AzureOpenAIChatClient

from data.cosmos_connection import CHALLENGE_DATABASE_NAME, close_cosmos_client, get_cosmos_database_client


CUSTOMER_BEHAVIOR_CONTAINER = "customer_behaviors"


def _strip_system_fields(value):
    if isinstance(value, dict):
        return {k: _strip_system_fields(v) for k, v in value.items() if not k.startswith("_")}
    if isinstance(value, list):
        return [_strip_system_fields(item) for item in value]
    return value


@tool
def search_customer_behavior(
    customer_id: Annotated[str, "Customer ID to query in customer_behavior collection"],
) -> str:
    """Search customer_behavior records in Cosmos DB by customer_id."""
    try:
        client, database = get_cosmos_database_client()
        container = database.get_container_client(CUSTOMER_BEHAVIOR_CONTAINER)
        query = "SELECT * FROM c WHERE c.customer_id = @customer_id"
        parameters = [{"name": "@customer_id", "value": customer_id}]
        items = list(
            container.query_items(
                query=query,
                parameters=parameters,
                partition_key=customer_id,
            )
        )

        if not items:
            return f"No customer_behaviors records found for customer_id={customer_id}."

        sanitized = _strip_system_fields(items[:20])
        return json.dumps(sanitized, ensure_ascii=False, default=str)
    except Exception as exc:
        return (
            f"Error querying {CHALLENGE_DATABASE_NAME}.{CUSTOMER_BEHAVIOR_CONTAINER} "
            f"for customer_id={customer_id}: {exc}"
        )
    finally:
        if "client" in locals():
            close_cosmos_client(client)


class BehavioralPatternAgent(AgentExecutor):
    INSTRUCTIONS = """
Eres un analista de fraudes en transacciones de un banco.
Debes extraer el customer_id desde la transacción de entrada y usar la herramienta search_customer_behavior para consultar el historial en la colección customer_behavior.
Analiza la transacciòn proporcionado, comparando la trayectoria de comportamiento del cliente para detectar patrones anómalos o inconsistentes con su historial de transacciones.
Proporciona un juicio sobre el nivel de riesgo asociado con la transacción, destacando cualquier señal de alerta o preocupación relevante.
Sé breve pero conciso.
"""

    def __init__(self, client: AzureOpenAIChatClient, name: str = "behavioral_pattern"):
        agent = client.as_agent(
            name=name,
            instructions=self.INSTRUCTIONS,
            tools=[search_customer_behavior],
        )
        super().__init__(agent=agent, id=name)
