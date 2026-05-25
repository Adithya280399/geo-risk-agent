import os, logging, psycopg2
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
log = logging.getLogger(__name__)

def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

def run(threshold: int = 5) -> dict:
    log.info(f"MonitorAgent: scanning for risk score >= {threshold}")
    conn = get_db()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT a.id, a.title, a.source, r.risk_category,
                   r.risk_score, r.countries
            FROM article_risk r
            JOIN articles a ON a.id = r.article_id
            WHERE r.risk_score >= %s
            ORDER BY r.risk_score DESC
            LIMIT 20
        """, (threshold,))
        rows = cur.fetchall()

    alerts = []
    for row in rows:
        article_id, title, source, category, score, countries = row
        alerts.append({
            "article_id":    article_id,
            "title":         title,
            "source":        source,
            "risk_category": category,
            "risk_score":    score,
            "countries":     countries or [],
        })

        with conn.cursor() as cur:
            for country in (countries or []):
                cur.execute("""
                    INSERT INTO risk_alerts
                        (country, risk_category, risk_score, headline, article_id)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (country, category, score, title, article_id))
        conn.commit()

    conn.close()
    log.info(f"MonitorAgent: found {len(alerts)} high-risk articles")

    return {
        "agent":   "monitor",
        "alerts":  alerts,
        "count":   len(alerts),
        "summary": f"Found {len(alerts)} articles with risk score >= {threshold}"
    }