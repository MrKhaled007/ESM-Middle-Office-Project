-- Risk limit utilisation with RAG status per country
SELECT
    b.country,
    ROUND(SUM(b.market_value_EUR) / 1e6, 2)        AS current_exposure_MEUR,
    ROUND(r.limit_EUR / 1e6, 2)                    AS limit_MEUR,
    ROUND(SUM(b.market_value_EUR) /
          r.limit_EUR * 100, 2)                     AS utilisation_pct,
    CASE
        WHEN SUM(b.market_value_EUR) /
             r.limit_EUR * 100 >= 90 THEN 'RED'
        WHEN SUM(b.market_value_EUR) /
             r.limit_EUR * 100 >= 70 THEN 'AMBER'
        ELSE 'GREEN'
    END AS rag_status
FROM bonds b
JOIN risk_limits r ON b.country = r.country
GROUP BY b.country
ORDER BY utilisation_pct DESC;