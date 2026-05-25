import streamlit as st
import os, psycopg2
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
st.set_page_config(page_title="Intelligence", page_icon="🤖", layout="wide")
st.title("🤖 Intelligence Agent")

def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_HOST"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

tab1, tab2 = st.tabs(["Generate Brief", "Past Briefs"])

with tab1:
    st.subheader("Generate Intelligence Brief")
    st.markdown("Enter a geopolitical query and the AI agent will retrieve relevant articles and generate a structured brief.")

    query = st.text_area(
        "Query",
        placeholder="e.g. What are the biggest military risks in the Middle East?",
        height=100
    )

    col1, col2 = st.columns(2)
    with col1:
        use_orchestrator = st.checkbox(
            "Run full multi-agent report",
            help="Runs MonitorAgent + CountryAgent + ReportAgent for a comprehensive report"
        )
    with col2:
        if st.button("Generate", type="primary", disabled=not query):
            with st.spinner("Agents working..."):
                try:
                    if use_orchestrator:
                        from agents.orchestrator import run as orchestrator_run
                        result = orchestrator_run(query)
                        st.success(f"Report complete — {result['monitor_alerts']} alerts, "
                                   f"{result['countries_profiled']} countries profiled")
                        st.markdown(result["report"])
                        st.caption(f"Generated in {result['total_duration_ms']}ms")
                    else:
                        from rag.brief_generator import generate_brief
                        result = generate_brief(query)
                        st.success(f"Brief generated from {result['articles_used']} articles")
                        st.markdown(result["brief"])
                        st.caption(f"Countries: {', '.join(result['countries'][:5])}")
                except Exception as e:
                    st.error(f"Error: {e}")

with tab2:
    st.subheader("Previously Generated Briefs")
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT query, brief, risk_category, countries, created_at
                FROM risk_briefs
                ORDER BY created_at DESC
                LIMIT 20
            """)
            briefs = cur.fetchall()
        conn.close()

        if not briefs:
            st.info("No briefs generated yet. Use the Generate Brief tab above.")
        else:
            for query_text, brief, category, countries, created_at in briefs:
                with st.expander(f"[{str(created_at)[:16]}] {query_text[:70]}"):
                    if category:
                        st.caption(f"Category: {category.upper()} | "
                                   f"Countries: {', '.join((countries or [])[:4])}")
                    st.markdown(brief)

    except Exception as e:
        st.error(f"Error loading briefs: {e}")