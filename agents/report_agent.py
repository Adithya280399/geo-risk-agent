import os, logging, psycopg2, time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from rag.retriever import retrieve

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
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

def run(query: str, monitor_result: dict, country_results: list[dict]) -> dict:
    log.info(f"ReportAgent: compiling final report for '{query}'")
    start = time.time()

    articles      = retrieve(query, top_k=6)
    article_ids   = [a["id"] for a in articles]

    monitor_summary  = monitor_result.get("summary", "")
    country_summaries = "\n".join(
        f"- {r['country']}: {r['summary']}" for r in country_results
    )
    article_context = "\n".join(
        f"[{a['title']}] Risk: {a['risk_category']} {a['risk_score']}/10 | "
        f"Countries: {', '.join(a['countries'])}"
        for a in articles
    )

    prompt = f"""You are a senior geopolitical risk analyst compiling an executive report.

QUERY: {query}

MONITORING ALERTS:
{monitor_summary}
High-risk articles found: {monitor_result.get('count', 0)}

COUNTRY ANALYSIS:
{country_summaries}

SUPPORTING ARTICLES:
{article_context}

Generate a comprehensive EXECUTIVE RISK REPORT with:

# EXECUTIVE RISK REPORT

## OVERVIEW
(2-3 sentences on the overall geopolitical situation)

## HIGH PRIORITY ALERTS
(List top 3 most critical risks with country, category, and severity)

## COUNTRY RISK PROFILES
(Brief risk profile for each analysed country)

## STRATEGIC IMPLICATIONS
(What does this mean for global stability, trade, energy?)

## RECOMMENDED ACTIONS
(3 concrete recommendations for risk mitigation)

## OVERALL RISK RATING
(Rate as: STABLE / ELEVATED / HIGH / CRITICAL with justification)

Be direct, analytical, and actionable."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=900,
    )

    report      = response.choices[0].message.content
    duration_ms = int((time.time() - start) * 1000)

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO agent_runs
                (agent_name, query, result, articles_used, duration_ms)
            VALUES (%s, %s, %s, %s, %s)
        """, ("report_agent", query, report, article_ids, duration_ms))
    conn.commit()
    conn.close()

    return {
        "agent":       "report",
        "query":       query,
        "report":      report,
        "duration_ms": duration_ms,
        "articles_used": len(articles),
    }