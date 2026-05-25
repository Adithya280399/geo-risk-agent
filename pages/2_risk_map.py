import streamlit as st
import os, psycopg2, plotly.express as px, plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
st.set_page_config(page_title="Risk Map", page_icon="🗺️", layout="wide")
st.title("🗺️ Country Risk Map")

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
        cur.execute("""
            SELECT
                UNNEST(countries) as country,
                AVG(risk_score)   as avg_score,
                COUNT(*)          as article_count,
                MODE() WITHIN GROUP (ORDER BY risk_category) as top_category
            FROM article_risk
            WHERE array_length(countries, 1) > 0
            GROUP BY country
            HAVING COUNT(*) >= 2
            ORDER BY avg_score DESC
            LIMIT 30
        """)
        rows = cur.fetchall()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT risk_category, COUNT(*), ROUND(AVG(risk_score), 1)
            FROM article_risk
            GROUP BY risk_category
            ORDER BY count DESC
        """)
        cat_rows = cur.fetchall()

    conn.close()

    df = pd.DataFrame(rows, columns=["country", "avg_score", "article_count", "top_category"])
    df["avg_score"] = df["avg_score"].astype(float).round(1)

    st.subheader("Top Countries by Risk Score")
    fig_bar = px.bar(
        df.head(15),
        x="country",
        y="avg_score",
        color="top_category",
        color_discrete_map={
            "military":  "#EF4444",
            "economic":  "#F97316",
            "political": "#EAB308",
            "energy":    "#8B5CF6",
            "general":   "#6B7280",
        },
        labels={"avg_score": "Avg Risk Score", "country": "Country"},
        height=400
    )
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Risk Category Breakdown")
        cat_df = pd.DataFrame(cat_rows, columns=["category", "count", "avg_score"])
        fig_pie = px.pie(
            cat_df,
            values="count",
            names="category",
            color="category",
            color_discrete_map={
                "military":  "#EF4444",
                "economic":  "#F97316",
                "political": "#EAB308",
                "energy":    "#8B5CF6",
                "general":   "#6B7280",
            },
            height=350
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("Country Risk Table")
        st.dataframe(
            df[["country", "avg_score", "article_count", "top_category"]].rename(columns={
                "country":      "Country",
                "avg_score":    "Avg Risk Score",
                "article_count":"Articles",
                "top_category": "Primary Risk",
            }),
            use_container_width=True,
            height=350
        )

except Exception as e:
    st.error(f"Error: {e}")