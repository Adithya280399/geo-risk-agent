import streamlit as st
import os, psycopg2
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
st.set_page_config(page_title="Live Feed", page_icon="📰", layout="wide")
st.title("📰 Live Article Feed")

def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

col1, col2, col3 = st.columns(3)
with col1:
    category_filter = st.selectbox(
        "Risk Category",
        ["All", "military", "economic", "political", "energy", "general"]
    )
with col2:
    min_score = st.slider("Minimum Risk Score", 1, 10, 1)
with col3:
    limit = st.selectbox("Show", [25, 50, 100], index=0)

try:
    conn = get_db()
    query = """
        SELECT a.id, a.title, a.source, a.url, a.published_at,
               r.risk_category, r.risk_score, r.countries
        FROM articles a
        JOIN article_risk r ON a.id = r.article_id
        WHERE r.risk_score >= %s
    """
    params = [min_score]

    if category_filter != "All":
        query += " AND r.risk_category = %s"
        params.append(category_filter)

    query += " ORDER BY r.risk_score DESC, a.published_at DESC LIMIT %s"
    params.append(limit)

    with conn.cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()
    conn.close()

    st.markdown(f"**{len(rows)} articles found**")
    st.markdown("---")

    CATEGORY_COLORS = {
        "military":  "🔴",
        "economic":  "🟠",
        "political": "🟡",
        "energy":    "🟣",
        "general":   "⚪",
    }

    for row in rows:
        aid, title, source, url, published_at, category, score, countries = row
        emoji = CATEGORY_COLORS.get(category, "⚪")

        with st.expander(f"{emoji} [{score}/10] {title[:80]}"):
            col_a, col_b, col_c = st.columns(3)
            col_a.markdown(f"**Source:** {source}")
            col_b.markdown(f"**Category:** {category.upper()}")
            col_c.markdown(f"**Risk Score:** {score}/10")

            if countries:
                st.markdown(f"**Countries:** {', '.join(countries[:5])}")
            if published_at:
                st.markdown(f"**Published:** {str(published_at)[:16]}")
            if url:
                st.markdown(f"[Read full article]({url})")

except Exception as e:
    st.error(f"Error: {e}")