import json
import os
from typing import Annotated

from agent_framework import AgentExecutor, tool
from agent_framework.azure import AzureOpenAIChatClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI

from data.cosmos_connection import CHALLENGE_DATABASE_NAME, close_cosmos_client, get_cosmos_database_client


FRAUD_POLICIES_INDEX_NAME = "fraud_policies_index"
FRAUD_POLICIES_VECTOR_FIELD = "rule_vector"
CUSTOMER_BEHAVIOR_CONTAINER = "customer_behaviors"


def _get_embedding(text: str) -> list[float]:
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
    api_version = "2023-05-15"
    api_key = os.getenv("AZURE_OPENAI_API_KEY")

    if not endpoint or not deployment:
        raise ValueError(
            "Azure OpenAI embedding config missing. Set AZURE_OPENAI_ENDPOINT and "
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME."
        )

    if api_key:
        embedding_client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )
    else:
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default",
        )
        embedding_client = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version=api_version,
        )

    response = embedding_client.embeddings.create(
        model=deployment,
        input=text,
    )
    return response.data[0].embedding


def _get_search_client() -> SearchClient:
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")

    if not endpoint:
        raise ValueError(
            "Azure AI Search config missing. Set AZURE_SEARCH_ENDPOINT."
        )

    print(f"[internal_policy] Azure AI Search endpoint: {endpoint}")

    credential = AzureKeyCredential(api_key) if api_key else DefaultAzureCredential()
    search_client = SearchClient(endpoint=endpoint, index_name=FRAUD_POLICIES_INDEX_NAME, credential=credential)
    print("[internal_policy] Azure AI Search client created")
    return search_client


def _strip_system_fields(value):
    if isinstance(value, dict):
        return {k: _strip_system_fields(v) for k, v in value.items() if not k.startswith("@") and not k.startswith("_")}
    if isinstance(value, list):
        return [_strip_system_fields(item) for item in value]
    return value


@tool
def search_customer_behavior(
    customer_id: Annotated[str, "Customer ID to query in customer_behavior collection"],
) -> str:
    """Search customer behavior records in Cosmos DB by customer_id."""
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

        docs = _strip_system_fields(items[:20])
        return json.dumps(docs, ensure_ascii=False, default=str)
    except Exception as exc:
        return (
            f"Error querying {CHALLENGE_DATABASE_NAME}.{CUSTOMER_BEHAVIOR_CONTAINER} "
            f"for customer_id={customer_id}: {exc}"
        )
    finally:
        if "client" in locals():
            close_cosmos_client(client)


@tool
def search_internal_fraud_policies(
    transaction_text: Annotated[str, "The full transaction text to retrieve relevant internal fraud policies"],
) -> str:
    """Retrieve internal fraud policies from Azure AI Search using vector search over transaction context."""
    try:
        vector_field = os.getenv("AZURE_SEARCH_VECTOR_FIELD", FRAUD_POLICIES_VECTOR_FIELD)
        top_k = int(os.getenv("AZURE_SEARCH_TOP_K", "5"))

        query_vector = _get_embedding(transaction_text)
        vector_query = VectorizedQuery(
            vector=query_vector,
            k=top_k,
            fields=vector_field,
        )

        search_client = _get_search_client()
        results = search_client.search(
            search_text=None,
            vector_queries=[vector_query],
            top=top_k,
        )

        docs = [_strip_system_fields(dict(item)) for item in results]
        if not docs:
            return "No internal fraud policies found for this transaction context."

        return json.dumps(docs, ensure_ascii=False, default=str)
    except Exception as exc:
        return f"Error retrieving internal fraud policies from Azure AI Search: {exc}"


class InternalPolicyAgent(AgentExecutor):
    INSTRUCTIONS = """
Eres un analista de fraudes en transacciones de un banco.
Debes usar la herramienta search_internal_fraud_policies usando como entrada la transacción completa recibida.
También debes usar la herramienta search_customer_behavior extrayendo el customer_id de la transacción.
Consulta las políticas internas del banco relacionadas con la detección de fraudes usando los resultados recuperados.
En base a la transacción proporcionada, las políticas internas y el historial de comportamiento del cliente, evalúa si la transacción cumple con los criterios de seguridad establecidos o si presenta riesgos de fraude.
Cada policy tiene un código final (eg CHALLENGE, ESCALATE_TO_HUMAN) tu funcion es, dado el contexto, concluir el código que aplica o si no aplica ninguno.
Indica todos los datos del policy (policy_id, chunk_id, version) para citar tu respuesta.
"""

    def __init__(self, client: AzureOpenAIChatClient, name: str = "internal_policy"):
        agent = client.as_agent(
            name=name,
            instructions=self.INSTRUCTIONS,
            tools=[search_internal_fraud_policies, search_customer_behavior],
        )
        super().__init__(agent=agent, id=name)
