import os
import uuid
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from embeddings.embedder import get_embeddings
from ingestion.scraper import fetch_rss, scrape_article


endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")
index_name = "news-index"

client = SearchClient(endpoint, index_name, AzureKeyCredential(key))


def run_upload():
    articles = fetch_rss()
    articles = articles[:2]  # limit for demo

    documents = []

    for a in articles:
        content = scrape_article(a["link"])

        if isinstance(content, dict):
            content = content.get("text", "")

        if not content:
            continue

        embedding = get_embeddings([content])[0]

        documents.append({
            "id": str(uuid.uuid4()),
            "title": a["title"],
            "content": content,
            "published": a.get("published", ""),
            "contentVector": embedding
        })

    if documents:
        client.upload_documents(documents)
        print(f"Uploaded {len(documents)} articles")
    else:
        print("No documents to upload")


if __name__ == "__main__":
    run_upload()