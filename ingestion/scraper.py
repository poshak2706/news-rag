import requests
import trafilatura
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def fetch_with_retry(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            return response.text
        except Exception as e:
            print(f"Retry {attempt+1} for {url}: {e}")
            time.sleep(2)

    return None


def scrape_article(url):
    try:
        html = fetch_with_retry(url)

        if not html:
            return {"text": ""}

        text = trafilatura.extract(html)

        return {"text": text or ""}

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {"text": ""}