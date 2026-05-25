# Geopolitical Risk Intelligence Agent

A real-time AI-powered geopolitical risk monitoring system that ingests live news, extracts entities, classifies risk, and generates executive intelligence briefs using a multi-agent pipeline.

## Architecture
News APIs → Kafka → PostgreSQL → spaCy NLP → FAISS → LangChain Agents → Streamlit

## What it does

- **Ingests** live news from NewsAPI and GNews across geopolitical queries
- **Streams** articles through Apache Kafka into PostgreSQL
- **Extracts** named entities (countries, organizations, people) using spaCy
- **Classifies** each article into military / economic / political / energy risk categories
- **Embeds** all articles into a FAISS vector index using OpenAI embeddings
- **Retrieves** semantically relevant articles for any natural language query
- **Generates** structured intelligence briefs using GPT-4o-mini via LangChain
- **Orchestrates** a 3-agent pipeline: MonitorAgent → CountryAgent → ReportAgent
- **Visualises** everything in a Streamlit dashboard with live filters and charts

## Tech Stack

| Layer | Technology |
|---|---|
| Data ingestion | NewsAPI, GNews, Apache Kafka |
| Storage | PostgreSQL 15 (Docker) |
| NLP | spaCy en_core_web_sm |
| Vector search | FAISS + OpenAI text-embedding-3-small |
| AI generation | GPT-4o-mini via LangChain |
| Agent framework | LangChain multi-agent orchestration |
| Dashboard | Streamlit + Plotly |
| Infrastructure | Docker, Docker Compose |

## Project Structure

geo-risk-agent/
├── ingestion/          # Kafka producer and consumer
├── nlp/                # Entity extraction and risk classification
├── rag/                # FAISS embedder, retriever, brief generator
├── agents/             # Orchestrator, monitor, country, report agents
├── db/                 # SQL schemas for all tables
├── pages/              # Streamlit dashboard pages
└── streamlit_app.py    # Main dashboard entry point

geo-risk-agent/
├── ingestion/          # Kafka producer and consumer
├── nlp/                # Entity extraction and risk classification
├── rag/                # FAISS embedder, retriever, brief generator
├── agents/             # Orchestrator, monitor, country, report agents
├── db/                 # SQL schemas for all tables
├── pages/              # Streamlit dashboard pages
└── streamlit_app.py    # Main dashboard entry point