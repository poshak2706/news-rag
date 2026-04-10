from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
import os
from dotenv import load_dotenv
from embeddings.embedder import get_embeddings

load_dotenv()

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")
index_name = "news-index"

client = SearchClient(endpoint, index_name, AzureKeyCredential(key))


def search_azure(query, k=10):
    vector = get_embeddings([query])[0]

    vector_query = VectorizedQuery(
        vector=vector,
        k_nearest_neighbors=k,
        fields="contentVector"
    )

    results = client.search(
        search_text=None,
        vector_queries=[vector_query]
    )

    seen_titles = set()
    output = []

    for r in results:
        title = r["title"]

        if title in seen_titles:
            continue

        seen_titles.add(title)

        output.append({
            "title": title,
            "content": r["content"],
            "published": r.get("published", ""),
            "link": r.get("link", "")

        })

        # limit final unique results
        if len(output) == 5:
            break

    return output