# SSENSE Analytics

A small project looking at how luxury fashion brands price themselves on SSENSE
(a Montreal-based multi-brand retailer that carries everything from Acne Studios
to Balenciaga). Built with Python, SQL, and a simple interactive dashboard.

Open `index.html` in a browser to play with it — no server, no install, just
double click it. Flip the tier switches on the right and the brand list and
charts update live.

Note on the data: SSENSE doesn't publish an official dataset, so this uses a
synthetic sample I generated (`generate_sample_data.py`) that copies the shape
of the real scraped dataset on Kaggle (title, brand, price, gender,
availability, ~78k rows). The whole pipeline runs fine on the sample data as-is.
If you want real numbers, download the actual CSV from Kaggle and swap it in
(instructions below).

## What I wanted to find out

- Do brands actually cluster into clear price tiers, or is it more of a gradient?
- Which product categories are the most expensive across the board (bags vs. tops vs. footwear, etc.)?
- Is there a price gap between men's and women's items in the same category?
- Which brands sell out more — is that a decent proxy for demand?
- Some brands carry way more SKUs than others — how deep does the assortment go per brand?

There's no category column in the raw data, so part of the cleaning step is
just pulling category out of the product title with some regex (jacket, boots,
tote bag, etc.) — not perfect, but good enough to group things sensibly.

## How it fits together

```
ssense_sample.csv   (or the real Kaggle CSV)
        │
        ▼  01_clean_data.py     — cleans up the data, extracts category from title
ssense_clean.csv
        │
        ├─▶ 02_analyze.py       — answers the 5 questions, writes analysis.json
        │
        ├─▶ load_to_sql.py      — dumps it into a SQLite db
        │        └─▶ queries.sql
        │
        └─▶ 03_build_website.py — bakes the data into index.html
```

## Running it

```bash
pip install -r requirements.txt

python generate_sample_data.py   # skip once you have the real CSV
python 01_clean_data.py
python 02_analyze.py
python load_to_sql.py
python 03_build_website.py

open index.html
```

## Swapping in the real dataset

1. Grab the CSV from [Kaggle](https://www.kaggle.com/datasets/justinpakzad/ssense-fashion-dataset), save it here as `ssense_real.csv`.
2. `python 01_clean_data.py --input ssense_real.csv`
3. Re-run the rest of the steps above.

Brands not already in the `BRAND_TIERS` mapping (in `02_analyze.py` and
`03_build_website.py`) fall back to a price-based guess for their tier —
worth extending that dict by hand if you want it more accurate.

## Power BI

`queries.sql` works fine as a SQL source against `ssense.db` (SQLite ODBC
driver), or just import `ssense_clean.csv` directly and rebuild the same
charts there.

## Stack

Python (pandas), SQLite, HTML/CSS/JS (Chart.js), optionally Power BI.

## Files

- `generate_sample_data.py` — makes the synthetic dataset
- `01_clean_data.py` — cleaning + category extraction
- `02_analyze.py` — the 5 analyses → `analysis.json`
- `load_to_sql.py` — loads cleaned data into SQLite
- `03_build_website.py` — builds `index.html`
- `schema.sql`, `queries.sql` — SQLite schema and the 5 questions as SQL
- `template.html` — source for the site (edit this, not index.html)
- `index.html` — the actual dashboard, open this one
