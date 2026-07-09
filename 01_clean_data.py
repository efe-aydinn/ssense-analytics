"""
01_clean_data.py

Cleans a raw SSENSE-style product CSV (real Kaggle export or the synthetic
sample) and extracts a `category` column from the free-text `title`, since
the raw schema has no category field. Writes ssense_clean.csv.

Usage:
    python 01_clean_data.py                      # uses ssense_sample.csv
    python 01_clean_data.py --input path/to.csv   # use the real Kaggle CSV
"""

import argparse
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent

# keyword -> category, checked against the title (case-insensitive).
# Order matters: more specific keywords should come first.
CATEGORY_KEYWORDS = [
    (r"\b(jacket|coat|parka|bomber|trench)\b", "Outerwear"),
    (r"\b(sweater|cardigan|knit|turtleneck)\b", "Knitwear"),
    (r"\b(sneaker|boots?|loafers?|sandals?|derby|shoes?)\b", "Footwear"),
    (r"\b(tote|crossbody|backpack|shoulder bag|bag)\b", "Bags"),
    (r"\b(t-shirt|tee|shirt|polo|tank)\b", "Tops"),
    (r"\b(jeans|denim)\b", "Denim"),
    (r"\b(trousers?|shorts?|cargo|track pants?|pants?)\b", "Bottoms"),
    (r"\b(belt|hat|scarf|gloves?|wallet)\b", "Accessories"),
]


def extract_category(title: str) -> str:
    t = str(title).lower()
    for pattern, category in CATEGORY_KEYWORDS:
        if re.search(pattern, t):
            return category
    return "Other"


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # basic hygiene
    df = df.drop_duplicates(subset=["item_id"]) if "item_id" in df.columns else df.drop_duplicates()
    df["brand"] = df["brand"].astype(str).str.strip()
    df["title"] = df["title"].astype(str).str.strip()

    # price: coerce to numeric, drop rows with no usable price
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df[df["price"].notna() & (df["price"] > 0)]

    # gender: normalize casing, fill missing as Unisex
    if "gender" in df.columns:
        df["gender"] = df["gender"].astype(str).str.title().replace({"Nan": "Unisex"})
    else:
        df["gender"] = "Unisex"

    # availability: normalize
    if "availability" in df.columns:
        df["availability"] = df["availability"].astype(str).str.title()
    else:
        df["availability"] = "Unknown"

    # category extraction from title
    df["category"] = df["title"].apply(extract_category)

    return df.reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=str(ROOT / "ssense_sample.csv"),
        help="Path to raw CSV (real Kaggle export or synthetic sample).",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "ssense_clean.csv"),
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    cleaned = clean(df)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(out_path, index=False)
    print(f"Cleaned {len(cleaned)} rows (from {len(df)} raw) -> {out_path}")
    print(cleaned["category"].value_counts())


if __name__ == "__main__":
    main()
