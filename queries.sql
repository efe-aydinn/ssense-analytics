-- queries.sql
-- The five core questions, answered directly in SQL against the `products`
-- table (see schema.sql / scripts/load_to_sql.py). Mirrors the logic in
-- scripts/02_analyze.py, so you can cross-check the Python output or plug
-- these straight into Power BI as a SQL source.

-- 1. Brand price positioning: median price per brand
SELECT
    brand,
    COUNT(*)                                   AS sku_count,
    ROUND(AVG(price), 2)                       AS avg_price,
    ROUND(MIN(price), 2)                       AS min_price,
    ROUND(MAX(price), 2)                       AS max_price
FROM products
GROUP BY brand
ORDER BY avg_price DESC;

-- 2. Category price distribution
SELECT
    category,
    COUNT(*)                                   AS n,
    ROUND(AVG(price), 2)                       AS avg_price,
    ROUND(MIN(price), 2)                       AS min_price,
    ROUND(MAX(price), 2)                       AS max_price
FROM products
GROUP BY category
ORDER BY avg_price DESC;

-- 3. Gender pricing gap by category
SELECT
    category,
    ROUND(AVG(CASE WHEN gender = 'Men' THEN price END), 2)   AS avg_price_men,
    ROUND(AVG(CASE WHEN gender = 'Women' THEN price END), 2) AS avg_price_women,
    ROUND(
        100.0 * (AVG(CASE WHEN gender = 'Men' THEN price END)
                - AVG(CASE WHEN gender = 'Women' THEN price END))
        / AVG(CASE WHEN gender = 'Women' THEN price END), 1
    ) AS gap_pct
FROM products
WHERE gender IN ('Men', 'Women')
GROUP BY category
ORDER BY gap_pct DESC;

-- 4. Availability / stock-out rate by brand
SELECT
    brand,
    COUNT(*)                                                          AS total_skus,
    SUM(CASE WHEN availability = 'Sold Out' THEN 1 ELSE 0 END)        AS sold_out_skus,
    ROUND(100.0 * SUM(CASE WHEN availability = 'Sold Out' THEN 1 ELSE 0 END)
          / COUNT(*), 1)                                              AS sold_out_pct
FROM products
GROUP BY brand
ORDER BY sold_out_pct DESC;

-- 5. Brand assortment depth (breadth of SKUs and price range)
SELECT
    brand,
    COUNT(*)                                   AS sku_count,
    ROUND(MAX(price) - MIN(price), 2)          AS price_range
FROM products
GROUP BY brand
ORDER BY sku_count DESC;
