import os, json, logging, psycopg2, faiss, numpy as np
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FAISS_INDEX_PATH    = "faiss_index/articles.index"
FAISS_METADATA_PATH = "faiss_index/articles_metadata.json"
EMBED_MODEL         = "text-embedding-3-small"

def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

def get_articles(conn) -> list[dict]:
    sql = """
        SELECT a.id, a.title, a.description, a.source,
               a.published_at, r.risk_category, r.risk_score, r.countries
        FROM articles a
        JOIN article_risk r ON a.id = r.article_id
        ORDER BY a.id
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return [
        {
            "id":            row[0],
            "title":         row[1] or "",
            "description":   row[2] or "",
            "source":        row[3] or "",
            "published_at":  str(row[4]),
            "risk_category": row[5],
            "risk_score":    row[6],
            "countries":     row[7] or [],
        }
        for row in rows
    ]

def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts
    )
    return [item.embedding for item in response.data]

def build_index():
    Path("faiss_index").mkdir(exist_ok=True)
    conn     = get_db()
    articles = get_articles(conn)
    conn.close()

    log.info(f"Embedding {len(articles)} articles...")

    texts = [
        f"{a['title']} {a['description']} risk:{a['risk_category']} countries:{' '.join(a['countries'])}"
        for a in articles
    ]

    batch_size  = 50
    embeddings  = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        vecs  = embed_texts(batch)
        embeddings.extend(vecs)
        log.info(f"Embedded {min(i + batch_size, len(texts))}/{len(texts)} articles")

    matrix = np.array(embeddings, dtype="float32")
    dim    = matrix.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(matrix)

    faiss.write_index(index, FAISS_INDEX_PATH)
    log.info(f"FAISS index saved — {index.ntotal} vectors, dim={dim}")

    with open(FAISS_METADATA_PATH, "w") as f:
        json.dump(articles, f, indent=2)
    log.info(f"Metadata saved to {FAISS_METADATA_PATH}")

if __name__ == "__main__":
    build_index()