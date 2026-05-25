import os, logging, psycopg2
from pathlib import Path
from dotenv import load_dotenv
from rag.retriever import retrieve

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

def run(country: str) -> dict:
    log.info(f"CountryAgent: analysing '{country}'")
    conn = get_db()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT a.id, a.title, r.risk_category, r.risk_score
            FROM article_risk r
            JOIN articles a ON a.id = r.article_id
            WHERE %s = ANY(r.countries)
            ORDER BY r.risk_score DESC
            LIMIT 10
        """, (country,))
        db_articles = cur.fetchall()

    conn.close()

    semantic = retrieve(f"geopolitical risk {country}", top_k=5)

    risk_scores    = [row[3] for row in db_articles]
    avg_score      = round(sum(risk_scores) / len(risk_scores), 1) if risk_scores else 0
    categories     = [row[2] for row in db_articles]
    top_category   = max(set(categories), key=categories.count) if categories else "unknown"

    return {
        "agent":        "country",
        "country":      country,
        "article_count": len(db_articles),
        "avg_risk_score": avg_score,
        "top_risk_category": top_category,
        "top_articles": [
            {"id": r[0], "title": r[1], "category": r[2], "score": r[3]}
            for r in db_articles[:5]
        ],
        "semantic_matches": len(semantic),
        "summary": (
            f"{country} appears in {len(db_articles)} articles. "
            f"Avg risk score: {avg_score}/10. "
            f"Primary risk type: {top_category.upper()}."
        )
    }