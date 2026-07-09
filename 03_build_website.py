"""
03_build_website.py

Builds a single self-contained HTML file (index.html) with the
cleaned + tiered product data embedded directly as JSON, so the page needs
no backend or fetch calls -- open it straight in a browser, or deploy the
one file to GitHub Pages.

Run this after 01_clean_data.py and 02_analyze.py.
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent

BRAND_TIERS = {
    "Acne Studios": "Entry-Luxury", "A.P.C.": "Entry-Luxury", "Ganni": "Entry-Luxury",
    "Axel Arigato": "Entry-Luxury", "AMI Paris": "Entry-Luxury", "Won Hundred": "Entry-Luxury",
    "Off-White": "Streetwear-Crossover", "Palm Angels": "Streetwear-Crossover",
    "Fear of God Essentials": "Streetwear-Crossover", "Stussy": "Streetwear-Crossover",
    "Marcelo Burlon": "Streetwear-Crossover", "Kenzo": "Streetwear-Crossover",
    "Jacquemus": "Contemporary", "Marni": "Contemporary", "Isabel Marant": "Contemporary",
    "Ferragamo": "Contemporary",
    "Rick Owens": "High-Luxury", "Comme des Garcons": "High-Luxury",
    "Maison Margiela": "High-Luxury", "Balenciaga": "High-Luxury",
    "Bottega Veneta": "High-Luxury", "Loewe": "High-Luxury", "The Row": "High-Luxury",
}


def build():
    df = pd.read_csv(ROOT / "ssense_clean.csv")
    df["tier"] = df["brand"].map(BRAND_TIERS).fillna("Contemporary")

    records = df[["brand", "tier", "category", "price", "gender", "availability"]].to_dict(orient="records")

    template_path = ROOT / "template.html"
    html = template_path.read_text()
    html = html.replace("__PRODUCT_DATA_JSON__", json.dumps(records))

    out_path = ROOT / "index.html"
    out_path.write_text(html)
    print(f"Built {out_path} with {len(records)} embedded records "
          f"({out_path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    build()
