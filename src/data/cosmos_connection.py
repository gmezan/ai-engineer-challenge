import os

from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential


CHALLENGE_DATABASE_NAME = "challenge-db"
_COSMOS_CLIENT: CosmosClient | None = None
_COSMOS_DATABASE = None


def get_cosmos_database_client() -> tuple[CosmosClient, object]:
    global _COSMOS_CLIENT, _COSMOS_DATABASE

    if _COSMOS_CLIENT is not None and _COSMOS_DATABASE is not None:
        return _COSMOS_CLIENT, _COSMOS_DATABASE

    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")

    if not endpoint:
        raise ValueError("Cosmos DB is not configured. Set COSMOS_ENDPOINT.")

    credential = key if key else DefaultAzureCredential()
    _COSMOS_CLIENT = CosmosClient(endpoint, credential=credential)
    _COSMOS_DATABASE = _COSMOS_CLIENT.get_database_client(CHALLENGE_DATABASE_NAME)
    return _COSMOS_CLIENT, _COSMOS_DATABASE


def close_cosmos_client(client: CosmosClient) -> None:
    return
