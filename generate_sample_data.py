"""
generate_sample_data.py

Generates a synthetic product catalog that mirrors the schema of the real
SSENSE Kaggle dataset (title, brand, price, currency, availability, item_id,
sku, description, gender, scraped_at) so the full pipeline can be built,
tested, and demoed before the real ~78k-row CSV is downloaded.

Brand price tiers below are set from public knowledge of each label's general
market positioning (illustrative, not scraped) purely to make the synthetic
data behave realistically. Swap this file out once data/raw/ssense_raw.csv
(the real Kaggle export) is in place -- 01_clean_data.py works on either.
"""

import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)

# brand -> (tier, [min_price, max_price] in USD)
BRANDS = {
    # Entry-luxury / accessible contemporary
    "Acne Studios":        ("Entry-Luxury", (120, 650)),
    "A.P.C.":               ("Entry-Luxury", (90, 500)),
    "Ganni":                ("Entry-Luxury", (100, 550)),
    "Axel Arigato":         ("Entry-Luxury", (110, 400)),
    "AMI Paris":            ("Entry-Luxury", (130, 600)),
    "Won Hundred":          ("Entry-Luxury", (80, 350)),

    # Streetwear-crossover
    "Off-White":            ("Streetwear-Crossover", (150, 1200)),
    "Palm Angels":          ("Streetwear-Crossover", (140, 950)),
    "Fear of God Essentials": ("Streetwear-Crossover", (90, 500)),
    "Stussy":               ("Streetwear-Crossover", (60, 300)),
    "Marcelo Burlon":       ("Streetwear-Crossover", (100, 600)),
    "Kenzo":                ("Streetwear-Crossover", (120, 800)),

    # Contemporary / mid luxury
    "Jacquemus":            ("Contemporary", (150, 1400)),
    "Marni":                ("Contemporary", (200, 1800)),
    "Isabel Marant":        ("Contemporary", (180, 1600)),
    "Ferragamo":            ("Contemporary", (250, 2200)),

    # High luxury
    "Rick Owens":           ("High-Luxury", (300, 3500)),
    "Comme des Garcons":    ("High-Luxury", (200, 2800)),
    "Maison Margiela":      ("High-Luxury", (250, 3200)),
    "Balenciaga":           ("High-Luxury", (350, 4500)),
    "Bottega Veneta":       ("High-Luxury", (400, 5500)),
    "Loewe":                ("High-Luxury", (300, 4800)),
    "The Row":              ("High-Luxury", (450, 6000)),
}

CATEGORIES = {
    "Outerwear":  ["Jacket", "Coat", "Parka", "Bomber Jacket", "Trench Coat"],
    "Knitwear":   ["Sweater", "Cardigan", "Knit Top", "Turtleneck"],
    "Footwear":   ["Sneakers", "Boots", "Loafers", "Sandals", "Derby Shoes"],
    "Bags":       ["Tote Bag", "Crossbody Bag", "Backpack", "Shoulder Bag"],
    "Tops":       ["T-Shirt", "Shirt", "Polo Shirt", "Tank Top"],
    "Bottoms":    ["Trousers", "Shorts", "Cargo Pants", "Track Pants"],
    "Denim":      ["Jeans", "Denim Jacket", "Denim Shorts"],
    "Accessories": ["Belt", "Hat", "Scarf", "Gloves", "Wallet"],
}

GENDERS = ["Men", "Women"]
AVAILABILITY = ["In Stock", "Low Stock", "Sold Out"]
# base probabilities, later perturbed per-brand to create differing sell-out rates
AVAIL_BASE_P = [0.70, 0.18, 0.12]

N_PRODUCTS = 6000


def sample_price(lo, hi, category, gender):
    """Log-uniform-ish price draw, with small category/gender multipliers
    so categories like Bags/Outerwear skew higher and a mild gender gap exists."""
    base = np.exp(RNG.uniform(np.log(lo), np.log(hi)))
    cat_mult = {
        "Bags": 1.15, "Outerwear": 1.10, "Footwear": 1.0, "Knitwear": 0.9,
        "Tops": 0.75, "Bottoms": 0.95, "Denim": 0.85, "Accessories": 0.6,
    }.get(category, 1.0)
    gender_mult = 1.06 if gender == "Men" else 1.0  # small synthetic gap to analyze
    return round(base * cat_mult * gender_mult, 2)


def main():
    rows = []
    brand_names = list(BRANDS.keys())
    # give each brand its own stock-out tendency (some brands run hotter/scarcer)
    brand_availability_skew = {b: RNG.uniform(0.6, 1.6) for b in brand_names}

    for i in range(N_PRODUCTS):
        brand = RNG.choice(brand_names)
        tier, (lo, hi) = BRANDS[brand]
        category = RNG.choice(list(CATEGORIES.keys()))
        item_type = RNG.choice(CATEGORIES[category])
        gender = RNG.choice(GENDERS)
        price = sample_price(lo, hi, category, gender)

        skew = brand_availability_skew[brand]
        p = np.array(AVAIL_BASE_P) ** (1 / skew)
        p = p / p.sum()
        availability = RNG.choice(AVAILABILITY, p=p)

        title = f"{brand} {item_type}"
        rows.append({
            "item_id": f"SS{100000 + i}",
            "sku": f"{brand[:3].upper()}-{RNG.integers(1000,9999)}",
            "title": title,
            "brand": brand,
            "price": price,
            "currency": "USD",
            "availability": availability,
            "gender": gender,
            "description": f"{item_type} by {brand}.",
            "scraped_at": "2026-06-15",
        })

    df = pd.DataFrame(rows)
    out_path = Path(__file__).resolve().parent / "ssense_sample.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} synthetic rows to {out_path}")


if __name__ == "__main__":
    main()
