import uuid
import hashlib
from ingestion.rss_fetcher import fetch_rss
from ingestion.scraper import scrape_article
from embeddings.embedder import get_embeddings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")

client = SearchClient(endpoint, "news-index", AzureKeyCredential(key))


def generate_id(text):
    return hashlib.md5(text.encode()).hexdigest()

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line=f"[{timestamp}] {msg}"
    print(line)
    os.makedirs("/app/logs", exist_ok=True)

    with open("/app/logs/logs.txt", "a") as f:
        f.write(line + "\n")


def run_pipeline():
    articles = fetch_rss()
    log("Auto: Fetching RSS Feed")
    articles = articles[:2]
    log(f"Auto: Retrieved {len(articles)} Articles")

    contents = []
    valid_articles = []

    for a in articles:
        content = scrape_article(a["link"])

        if isinstance(content, dict):
            content = content.get("text", "")

        if not content:
            continue

        contents.append(content)
        valid_articles.append(a)

    embeddings = get_embeddings(contents)

    documents = []

    for a, content, embedding in zip(valid_articles, contents, embeddings):
        documents.append({
            "id": generate_id(a["link"]),
            "title": a["title"],
            "content": content,
            "published": a.get("published", ""),
            "link": a.get("link", ""),
            "contentVector": embedding
        })

    if documents:
        client.merge_or_upload_documents(documents)

    log(f"Auto: Uploaded {len(documents)} articles")


if __name__ == "__main__":
    run_pipeline()