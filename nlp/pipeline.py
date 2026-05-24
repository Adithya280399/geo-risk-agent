import os, logging, psycopg2
from dotenv import load_dotenv
from pathlib import Path
from nlp.entity_extractor import extract_entities
from nlp.risk_classifier  import classify_risk

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
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

def get_unprocessed_articles(conn):
    sql = """
        SELECT a.id, a.title, a.description, a.content
        FROM articles a
        LEFT JOIN article_risk r ON a.id = r.article_id
        WHERE r.article_id IS NULL
        ORDER BY a.published_at DESC
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()

def save_entities(conn, article_id: int, entities: dict):
    sql = """
        INSERT INTO article_entities (article_id, entity_text, entity_type)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
    """
    with conn.cursor() as cur:
        for ent in entities["all_entities"]:
            cur.execute(sql, (article_id, ent["text"], ent["type"]))
    conn.commit()

def save_risk(conn, article_id: int, risk: dict, entities: dict):
    sql = """
        INSERT INTO article_risk
            (article_id, risk_category, risk_score, countries, organizations, people)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (article_id) DO NOTHING
    """
    with conn.cursor() as cur:
        cur.execute(sql, (
            article_id,
            risk["category"],
            risk["score"],
            entities["countries"],
            entities["organizations"],
            entities["people"],
        ))
    conn.commit()

def run_pipeline():
    conn = get_db()
    articles = get_unprocessed_articles(conn)
    log.info(f"Processing {len(articles)} unprocessed articles...")

    for article_id, title, description, content in articles:
        try:
            full_text = f"{title or ''} {description or ''} {content or ''}"
            entities  = extract_entities(full_text)
            risk      = classify_risk(title or "", description or "", content or "")

            save_entities(conn, article_id, entities)
            save_risk(conn, article_id, risk, entities)

            log.info(
                f"[{article_id}] {risk['category'].upper()} "
                f"score={risk['score']} "
                f"countries={entities['countries'][:3]} | "
                f"{(title or '')[:50]}"
            )
        except Exception as e:
            log.error(f"Failed article {article_id}: {e}")
            continue

    conn.close()
    log.info("NLP pipeline complete.")

if __name__ == "__main__":
    run_pipeline()