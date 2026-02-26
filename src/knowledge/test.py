import os

from azure.identity import AzureCliCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI

try:
	from dotenv import load_dotenv
except ImportError:
	def load_dotenv() -> None:
		return


load_dotenv()

INDEX_NAME = os.environ.get("SEARCH_INDEX_NAME", "fraud_policies_index")
SEARCH_ENDPOINT = os.environ.get("SEARCH_ENDPOINT")
if not SEARCH_ENDPOINT:
	raise ValueError("Environment variable SEARCH_ENDPOINT is required")

EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
if not EMBEDDING_DEPLOYMENT:
	raise ValueError("Environment variable AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME is required")

QUERY_TEXT = os.environ.get(
	"VECTOR_TEST_QUERY",
	"transacción internacional desde dispositivo nuevo",
)
TOP_K = int(os.environ.get("VECTOR_TEST_TOP_K", "3"))


def main() -> None:
	credential = AzureCliCredential()

	search_client = SearchClient(
		endpoint=SEARCH_ENDPOINT,
		index_name=INDEX_NAME,
		credential=credential,
	)

	openai_client = AzureOpenAI()

	emb_resp = openai_client.embeddings.create(
		model=EMBEDDING_DEPLOYMENT,
		input=QUERY_TEXT,
	)
	query_vector = emb_resp.data[0].embedding

	vector_query = VectorizedQuery(
		vector=query_vector,
		k_nearest_neighbors=TOP_K,
		fields="rule_vector",
	)

	results = search_client.search(
		search_text=None,
		vector_queries=[vector_query],
		top=TOP_K,
		select=["policy_id", "rule", "version"],
	)

	print(f"Query: {QUERY_TEXT}")
	print(f"Index: {INDEX_NAME}")
	print(f"Top K: {TOP_K}")
	print("Results:")

	found_any = False
	for idx, doc in enumerate(results, start=1):
		found_any = True
		score = doc.get("@search.score")
		print(f"{idx}. score={score}")
		print(f"   policy_id={doc.get('policy_id')}")
		print(f"   version={doc.get('version')}")
		print(f"   rule={doc.get('rule')}")

	if not found_any:
		print("No vector search results returned.")


if __name__ == "__main__":
	main()
