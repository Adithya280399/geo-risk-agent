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

## Setup

1. Clone the repo
2. Install Python 3.11 and Docker Desktop
3. Create `.env` with your API keys (see `.env.example`)
4. Start services: `docker-compose up -d`
5. Apply schemas: run all `db/schema*.sql` files
6. Install dependencies: `pip install -r requirements.txt`
7. Download spaCy model: `pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.6.0/en_core_web_sm-3.6.0-py3-none-any.whl`
8. Run ingestion: `python ingestion/collector.py`
9. Run NLP pipeline: `python -m nlp.pipeline`
10. Build FAISS index: `python -m rag.embedder`
11. Launch dashboard: `streamlit run streamlit_app.py`

## Environment Variables
NEWS_API_KEY=
GNEWS_API_KEY=
OPENAI_API_KEY=
KAFKA_BROKER=localhost:9092
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=georisk
POSTGRES_USER=admin
POSTGRES_PASSWORD=

## Built by

Adithya Suresh — M.S. Information Science, University of North Texas

