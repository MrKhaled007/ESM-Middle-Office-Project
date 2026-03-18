-- Total portfolio exposure and market value per country
SELECT
    country,
    COUNT(bond_id)                          AS num_bonds,
    ROUND(SUM(face_value_EUR) / 1e6, 2)    AS total_face_value_MEUR,
    ROUND(SUM(market_value_EUR) / 1e6, 2)  AS total_market_value_MEUR,
    ROUND(AVG(coupon_rate_pct), 2)          AS avg_coupon_pct
FROM bonds
GROUP BY country
ORDER BY total_market_value_MEUR DESC;