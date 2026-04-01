import json
from ingestion.rss_fetcher import fetch_rss
from ingestion.scraper import scrape_article
from processing.processor import process_articles

from embeddings.chunker import chunk_text
from embeddings.embedder import get_embeddings
from embeddings.vector_store import VectorStore
import time



def main():
    rss_articles = fetch_rss()

    full_articles = []

    for article in rss_articles[:50]:
        content = scrape_article(article["link"])
        time.sleep(1)

        if content and content["text"]:
            article.update(content)
            full_articles.append(article)

    print(f"Saved {len(full_articles)} articles.")

    processed_articles = process_articles(full_articles)

    print(f"Saved {len(processed_articles)} processed articles.")

    all_chunks = []
    metadata = []

    for article in processed_articles:
        chunks = chunk_text(article["cleaned_text"])

        for chunk in chunks:
            all_chunks.append(chunk)
            metadata.append({
                "title": article["title"],
                "content": chunk,
                "published": article.get("published", "")
            })

    embeddings = get_embeddings(all_chunks)

    store = VectorStore(len(embeddings[0]))
    store.add(embeddings, metadata)
    store.save()

    print("FAISS index created.")


if __name__ == "__main__":
    main()