import os, json, requests, logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from confluent_kafka import Producer

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

KAFKA_BROKER   = os.getenv("KAFKA_BROKER")
NEWS_API_KEY   = os.getenv("NEWS_API_KEY")
GNEWS_API_KEY  = os.getenv("GNEWS_API_KEY")
TOPIC          = "raw_articles"

producer = Producer({"bootstrap.servers": KAFKA_BROKER})

QUERIES = [
    "geopolitical conflict",
    "trade war sanctions",
    "military tension",
    "economic crisis government",
    "supply chain disruption",
]

def delivery_report(err, msg):
    if err:
        log.error(f"Delivery failed: {err}")
    else:
        log.info(f"Delivered to {msg.topic()} [{msg.partition()}]")

def fetch_newsapi(query: str) -> list[dict]:
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": NEWS_API_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        articles = r.json().get("articles", [])
        log.info(f"NewsAPI: {len(articles)} articles for '{query}'")
        return articles
    except Exception as e:
        log.error(f"NewsAPI error for '{query}': {e}")
        return []

def fetch_gnews(query: str) -> list[dict]:
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": query,
        "lang": "en",
        "max": 10,
        "token": GNEWS_API_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        articles = r.json().get("articles", [])
        log.info(f"GNews: {len(articles)} articles for '{query}'")
        return articles
    except Exception as e:
        log.error(f"GNews error for '{query}': {e}")
        return []

def normalize(article: dict, source_api: str) -> dict:
    if source_api == "newsapi":
        return {
            "title":        article.get("title", ""),
            "description":  article.get("description", ""),
            "content":      article.get("content", ""),
            "url":          article.get("url", ""),
            "source":       article.get("source", {}).get("name", ""),
            "published_at": article.get("publishedAt", ""),
            "fetched_at":   datetime.now(timezone.utc).isoformat(),
            "api_source":   "newsapi",
        }
    else:
        return {
            "title":        article.get("title", ""),
            "description":  article.get("description", ""),
            "content":      article.get("content", ""),
            "url":          article.get("url", ""),
            "source":       article.get("source", {}).get("name", ""),
            "published_at": article.get("publishedAt", ""),
            "fetched_at":   datetime.now(timezone.utc).isoformat(),
            "api_source":   "gnews",
        }

def publish(article: dict):
    producer.produce(
        TOPIC,
        key=article["url"].encode("utf-8"),
        value=json.dumps(article).encode("utf-8"),
        callback=delivery_report,
    )

def run_collection():
    log.info("Starting collection cycle...")
    seen_urls = set()
    total = 0

    for query in QUERIES:
        for article in fetch_newsapi(query):
            norm = normalize(article, "newsapi")
            if norm["url"] and norm["url"] not in seen_urls:
                seen_urls.add(norm["url"])
                publish(norm)
                total += 1

        for article in fetch_gnews(query):
            norm = normalize(article, "gnews")
            if norm["url"] and norm["url"] not in seen_urls:
                seen_urls.add(norm["url"])
                publish(norm)
                total += 1

    producer.flush()
    log.info(f"Collection cycle complete. Published {total} articles to Kafka.")

if __name__ == "__main__":
    run_collection()