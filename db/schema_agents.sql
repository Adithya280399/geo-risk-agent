CREATE TABLE IF NOT EXISTS agent_runs (
    id            SERIAL PRIMARY KEY,
    agent_name    TEXT NOT NULL,
    query         TEXT NOT NULL,
    result        TEXT NOT NULL,
    articles_used INTEGER[],
    duration_ms   INTEGER,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS risk_alerts (
    id            SERIAL PRIMARY KEY,
    country       TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    risk_score    INTEGER NOT NULL,
    headline      TEXT NOT NULL,
    article_id    INTEGER REFERENCES articles(id),
    alerted_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_runs_agent   ON agent_runs(agent_name);
CREATE INDEX IF NOT EXISTS idx_alerts_score ON risk_alerts(risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_country ON risk_alerts(country);