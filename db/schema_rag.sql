CREATE TABLE IF NOT EXISTS risk_briefs (
    id            SERIAL PRIMARY KEY,
    query         TEXT NOT NULL,
    brief         TEXT NOT NULL,
    risk_category TEXT,
    countries     TEXT[],
    article_ids   INTEGER[],
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_briefs_category ON risk_briefs(risk_category);
CREATE INDEX IF NOT EXISTS idx_briefs_created  ON risk_briefs(created_at DESC);