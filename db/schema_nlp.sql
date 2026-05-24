CREATE TABLE IF NOT EXISTS article_entities (
    id          SERIAL PRIMARY KEY,
    article_id  INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    entity_text TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS article_risk (
    id            SERIAL PRIMARY KEY,
    article_id    INTEGER REFERENCES articles(id) ON DELETE CASCADE UNIQUE,
    risk_category TEXT NOT NULL,
    risk_score    INTEGER NOT NULL CHECK (risk_score BETWEEN 1 AND 10),
    countries     TEXT[],
    organizations TEXT[],
    people        TEXT[],
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_entities_article ON article_entities(article_id);
CREATE INDEX IF NOT EXISTS idx_entities_type    ON article_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_risk_category    ON article_risk(risk_category);
CREATE INDEX IF NOT EXISTS idx_risk_score       ON article_risk(risk_score DESC);