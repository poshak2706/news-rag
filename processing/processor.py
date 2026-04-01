from processing.cleaner import clean_text
from processing.deduplicator import remove_duplicates

def process_articles(articles):
    processed = []
    print("Before filtering:", len(articles))

    for article in articles:
        cleaned_text = clean_text(article.get("text", ""))

        # Filter weak articles
        if len(cleaned_text) < 150:
            continue

        article["cleaned_text"] = cleaned_text
        processed.append(article)

    # Deduplicate
    processed = remove_duplicates(processed)

    return processed