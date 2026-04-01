import feedparser
from ingestion.sources import RSS_FEEDS
def is_valid_article(link):
    if "video" in link:
        return False
    if "newsfeed" in link:
        return False
    return True
def fetch_rss():
    articles = []

    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)

        for entry in feed.entries:
            if not is_valid_article(entry["link"]): 
                continue
            articles.append({
                "source": source,
                "title": entry.get("title"),
                "link": entry.get("link"),
                "published": entry.get("published", "")
            })

    return articles