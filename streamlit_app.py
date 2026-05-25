import streamlit as st

st.set_page_config(
    page_title="Geo Risk Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌍 Geopolitical Risk Intelligence Agent")
st.markdown("""
A real-time AI-powered geopolitical risk monitoring system built with:
**Kafka** · **PostgreSQL** · **spaCy NLP** · **FAISS** · **LangChain** · **GPT-4o-mini**
""")

col1, col2, col3, col4 = st.columns(4)

import os, psycopg2
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

try:
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM articles")
        article_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM article_risk")
        risk_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM risk_alerts")
        alert_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM risk_briefs")
        brief_count = cur.fetchone()[0]
    conn.close()

    col1.metric("Articles Ingested",   article_count,  "via Kafka")
    col2.metric("Articles Analysed",   risk_count,     "NLP pipeline")
    col3.metric("Risk Alerts",         alert_count,    "high priority")
    col4.metric("Briefs Generated",    brief_count,    "AI generated")

except Exception as e:
    st.error(f"Database connection error: {e}")

st.markdown("---")
st.markdown("""
### Navigate using the sidebar:
- **Live Feed** — Browse ingested articles with risk scores and filters
- **Risk Map** — Country risk profiles and category breakdown
- **Intelligence** — Run AI agents and generate intelligence briefs
""")