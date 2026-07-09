"""
load_to_sql.py

Loads ssense_clean.csv into a local SQLite database
(ssense.db) using the schema in schema.sql, so queries.sql (and
Power BI, via the SQLite ODBC driver) can query it directly.
"""

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent


def main():
    csv_path = ROOT / "ssense_clean.csv"
    db_path = ROOT / "ssense.db"
    schema_path = ROOT / "schema.sql"

    df = pd.read_csv(csv_path)
    keep_cols = [c for c in ["item_id", "sku", "title", "brand", "category",
                              "price", "currency", "gender", "availability",
                              "scraped_at"] if c in df.columns]
    df = df[keep_cols]

    conn = sqlite3.connect(db_path)
    conn.executescript(schema_path.read_text())
    df.to_sql("products", conn, if_exists="replace", index=False)
    conn.commit()

    n = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    print(f"Loaded {n} rows into {db_path}")
    conn.close()


if __name__ == "__main__":
    main()
