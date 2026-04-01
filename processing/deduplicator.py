def remove_duplicates(articles):
    seen_titles = set()
    unique_articles = []

    for article in articles:
        title = article.get("title", "").lower()

        if title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)

    return unique_articles