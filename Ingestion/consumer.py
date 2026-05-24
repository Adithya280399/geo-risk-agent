import os, json, logging, psycopg2
from dotenv import load_dotenv
from confluent_kafka import Consumer, KafkaError

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

def insert_article(conn, article: dict):
    sql = """
        INSERT INTO articles (title, description, content, url, source, published_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING
    """
    with conn.cursor() as cur:
        cur.execute(sql, (
            article.get("title"),
            article.get("description"),
            article.get("content"),
            article.get("url"),
            article.get("source"),
            article.get("published_at"),
        ))
    conn.commit()

def run_consumer():
    consumer = Consumer({
        "bootstrap.servers": os.getenv("KAFKA_BROKER"),
        "group.id":          "georisk-consumer-group",
        "auto.offset.reset": "earliest",
    })
    consumer.subscribe(["raw_articles"])
    conn = get_db()
    log.info("Consumer running — waiting for articles...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    log.error(f"Kafka error: {msg.error()}")
                continue
            article = json.loads(msg.value().decode("utf-8"))
            insert_article(conn, article)
            log.info(f"Stored: {article.get('title', '')[:60]}")
    except KeyboardInterrupt:
        log.info("Consumer stopped.")
    finally:
        consumer.close()
        conn.close()

if __name__ == "__main__":
    run_consumer()