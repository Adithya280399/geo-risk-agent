import os, logging, psycopg2
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from rag.retriever import retrieve

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

def generate_brief(query: str) -> dict:
    log.info(f"Retrieving articles for: '{query}'")
    articles = retrieve(query, top_k=8)

    context = ""
    for i, a in enumerate(articles, 1):
        context += (
            f"\n[{i}] {a['title']}\n"
            f"    Source: {a['source']} | "
            f"Risk: {a['risk_category'].upper()} (score {a['risk_score']}/10) | "
            f"Countries: {', '.join(a['countries']) if a['countries'] else 'N/A'}\n"
            f"    {a['description']}\n"
        )

    prompt = f"""You are a geopolitical risk intelligence analyst.
Based on the following news articles, generate a concise executive intelligence brief
answering this query: "{query}"

ARTICLES:
{context}

Write a structured brief with:
1. SITUATION SUMMARY (2-3 sentences)
2. KEY RISK FACTORS (bullet points)
3. COUNTRIES MOST AFFECTED
4. RISK ASSESSMENT (overall risk level: LOW/MEDIUM/HIGH/CRITICAL)
5. ANALYST RECOMMENDATION (1-2 sentences)

Be direct, factual, and use only information from the provided articles."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=600,
    )

    brief_text    = response.choices[0].message.content
    article_ids   = [a["id"] for a in articles]
    countries     = list(set(
        c for a in articles for c in (a["countries"] or [])
    ))
    risk_category = articles[0]["risk_category"] if articles else "general"

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO risk_briefs
               (query, brief, risk_category, countries, article_ids)
               VALUES (%s, %s, %s, %s, %s)""",
            (query, brief_text, risk_category, countries, article_ids)
        )
    conn.commit()
    conn.close()

    return {
        "query":         query,
        "brief":         brief_text,
        "articles_used": len(articles),
        "countries":     countries,
        "risk_category": risk_category,
    }

if __name__ == "__main__":
    queries = [
        "What are the biggest military risks in the Middle East right now?",
        "How are energy supply chains being disrupted by current conflicts?",
        "What is the current status of US-Iran relations?",
    ]
    for query in queries:
        result = generate_brief(query)
        print("\n" + "="*60)
        print(f"QUERY: {result['query']}")
        print("="*60)
        print(result["brief"])
        print(f"\nSources used: {result['articles_used']} articles")
        print(f"Countries: {', '.join(result['countries'][:5])}")