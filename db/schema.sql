CREATE TABLE IF NOT EXISTS articles (
    id          SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT,
    content     TEXT,
    url         TEXT UNIQUE,
    source      TEXT,
    country     TEXT,
    category    TEXT,
    published_at TIMESTAMPTZ,
    fetched_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_country   ON articles(country);.venv\Scripts\activate