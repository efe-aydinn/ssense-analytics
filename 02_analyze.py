"""
02_analyze.py

Runs the five core analyses on the cleaned dataset and writes a single JSON
file (analysis.json) that the interactive website reads
directly -- no backend needed, it's all baked into the JSON at build time.

    1. Brand price positioning (tiers)
    2. Category price distribution
    3. Gender pricing gap by category
    4. Availability / stock-out patterns
    5. Brand assortment depth
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent

# Manually curated tier labels for the brands used in the sample generator.
# When you swap in the real Kaggle dataset with different/more brands, extend
# this mapping (or replace with a clustering approach on median price).
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


def tier_for_brand(brand: str, median_price: float) -> str:
    if brand in BRAND_TIERS:
        return BRAND_TIERS[brand]
    # fallback heuristic for brands not in the manual map (e.g. real dataset)
    if median_price < 200:
        return "Entry-Luxury"
    if median_price < 450:
        return "Streetwear-Crossover"
    if median_price < 800:
        return "Contemporary"
    return "High-Luxury"


def q1_brand_tiers(df: pd.DataFrame) -> list:
    g = df.groupby("brand")["price"].agg(["median", "mean", "count"]).reset_index()
    g["tier"] = g.apply(lambda r: tier_for_brand(r["brand"], r["median"]), axis=1)
    g = g.sort_values("median", ascending=False)
    return g.round(2).to_dict(orient="records")


def q2_category_prices(df: pd.DataFrame) -> list:
    g = df.groupby("category")["price"].agg(["median", "mean", "min", "max", "count"]).reset_index()
    g = g.sort_values("median", ascending=False)
    return g.round(2).to_dict(orient="records")


def q3_gender_gap(df: pd.DataFrame) -> list:
    d = df[df["gender"].isin(["Men", "Women"])]
    g = d.groupby(["category", "gender"])["price"].median().unstack("gender")
    g = g.dropna()
    g["gap_pct"] = ((g["Men"] - g["Women"]) / g["Women"] * 100).round(1)
    g = g.reset_index().sort_values("gap_pct", ascending=False)
    return g.round(2).to_dict(orient="records")


def q4_availability(df: pd.DataFrame) -> dict:
    by_brand = (
        df.groupby("brand")["availability"]
        .apply(lambda s: (s == "Sold Out").mean() * 100)
        .round(1)
        .sort_values(ascending=False)
        .reset_index(name="sold_out_pct")
        .to_dict(orient="records")
    )
    by_category = (
        df.groupby("category")["availability"]
        .apply(lambda s: (s == "Sold Out").mean() * 100)
        .round(1)
        .sort_values(ascending=False)
        .reset_index(name="sold_out_pct")
        .to_dict(orient="records")
    )
    return {"by_brand": by_brand, "by_category": by_category}


def q5_assortment_depth(df: pd.DataFrame) -> list:
    g = df.groupby("brand")["price"].agg(sku_count="count", min_price="min", max_price="max").reset_index()
    g["price_range"] = (g["max_price"] - g["min_price"]).round(2)
    g = g.sort_values("sku_count", ascending=False)
    return g.round(2).to_dict(orient="records")


def main():
    in_path = ROOT / "ssense_clean.csv"
    df = pd.read_csv(in_path)

    result = {
        "meta": {
            "n_products": int(len(df)),
            "n_brands": int(df["brand"].nunique()),
            "n_categories": int(df["category"].nunique()),
            "note": "Synthetic sample data -- replace ssense_sample.csv with the real "
                    "Kaggle SSENSE CSV and re-run 01_clean_data.py and 02_analyze.py "
                    "to regenerate this file with real figures.",
        },
        "q1_brand_tiers": q1_brand_tiers(df),
        "q2_category_prices": q2_category_prices(df),
        "q3_gender_gap": q3_gender_gap(df),
        "q4_availability": q4_availability(df),
        "q5_assortment_depth": q5_assortment_depth(df),
    }

    out_path = ROOT / "analysis.json"
    out_path.write_text(json.dumps(result, indent=2))
    print(f"Wrote analysis JSON -> {out_path}")
    print(json.dumps(result["meta"], indent=2))


if __name__ == "__main__":
    main()
