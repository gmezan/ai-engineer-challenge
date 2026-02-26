import os
from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    HnswAlgorithmConfiguration,
    VectorSearch,
    VectorSearchProfile,
)
from azure.core.exceptions import ResourceNotFoundError
from openai import AzureOpenAI


load_dotenv()

index_name = "fraud_policies_index"
endpoint = os.environ.get("SEARCH_ENDPOINT")
if not endpoint:
    raise ValueError("Environment variable SEARCH_ENDPOINT is required")

credential = AzureCliCredential()

# helper clients
index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)

EMBEDDING_MODEL = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
openai_client = AzureOpenAI()

if not EMBEDDING_MODEL:
    raise ValueError("Environment variable AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME is required")

VECTOR_ALGORITHM_NAME = "fraud-hnsw"
VECTOR_PROFILE_NAME = "fraud-vector-profile"
VECTOR_DIMENSIONS = int(os.environ.get("AZURE_OPENAI_EMBEDDING_DIMENSIONS", "1536"))


def _build_index() -> SearchIndex:
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name=VECTOR_ALGORITHM_NAME,
            )
        ],
        profiles=[
            VectorSearchProfile(
                name=VECTOR_PROFILE_NAME,
                algorithm_configuration_name=VECTOR_ALGORITHM_NAME,
            )
        ],
    )

    fields = [
        SimpleField(name="policy_id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="rule", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
        SearchField(
            name="rule_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=VECTOR_DIMENSIONS,
            vector_search_profile_name=VECTOR_PROFILE_NAME,
        ),
        SimpleField(name="version", type=SearchFieldDataType.String, filterable=True),
    ]

    return SearchIndex(name=index_name, fields=fields, vector_search=vector_search)

def create_vector_index():
    """Create the search index with a vector field based on the rule text.

    The index will have a key field `policy_id`, a searchable `rule`
    field, and a vector field `rule_vector` containing the embedding for
    the rule content. If the index already exists this function is a no-op.
    """
    try:
        existing = index_client.get_index(index_name)

        fields_by_name = {field.name: field for field in existing.fields}
        vector_field = fields_by_name.get("rule_vector")
        vector_type = str(getattr(vector_field, "type", ""))
        vector_dims = getattr(vector_field, "vector_search_dimensions", None)

        if vector_field and vector_type == "Collection(Edm.Single)" and vector_dims == VECTOR_DIMENSIONS:
            print(f"Index '{index_name}' already exists with compatible schema, skipping creation.")
            return

        print(f"Index '{index_name}' exists but schema is incompatible. Recreating index...")
        index_client.delete_index(index_name)
    except ResourceNotFoundError:
        pass

    index = _build_index()
    index_client.create_index(index)
    print(f"Created index '{index_name}' with vector configuration.")


def upload_policies(filepath="fraud_policies.json"):
    """Load policies from JSON, compute embeddings, and upload to the index."""
    import json

    with open(filepath, "r") as f:
        docs = json.load(f)

    # compute embedding for each rule
    for doc in docs:
        try:
            emb_resp = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=doc["rule"])
            doc["rule_vector"] = emb_resp.data[0].embedding
        except Exception as exc:  # capture any HTTP errors
            print("Failed to generate embedding for rule:\n", doc["rule"])
            print("Error details:", exc)
            raise

    result = search_client.upload_documents(documents=docs)
    print("Upload result:", result)


if __name__ == "__main__":
    create_vector_index()
    upload_policies()

