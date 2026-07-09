-- schema.sql
-- Run against SQLite (or adapt types for Postgres/MySQL) to hold the cleaned
-- SSENSE product data before running the analysis queries.

CREATE TABLE IF NOT EXISTS products (
    item_id       TEXT PRIMARY KEY,
    sku           TEXT,
    title         TEXT NOT NULL,
    brand         TEXT NOT NULL,
    category      TEXT NOT NULL,
    price         REAL NOT NULL,
    currency      TEXT DEFAULT 'USD',
    gender        TEXT,
    availability  TEXT,
    scraped_at    TEXT
);

CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
