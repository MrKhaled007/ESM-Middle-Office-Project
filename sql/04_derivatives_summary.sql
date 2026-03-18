-- Active derivatives exposure by counterparty and instrument type
SELECT
    counterparty,
    type                                            AS instrument_type,
    COUNT(deriv_id)                                 AS num_contracts,
    ROUND(SUM(notional_EUR) / 1e6, 2)              AS total_notional_MEUR,
    ROUND(SUM(mtm_value_EUR) / 1e6, 4)             AS total_mtm_MEUR
FROM derivatives
WHERE status = 'Active'
GROUP BY counterparty, type
ORDER BY total_notional_MEUR DESC;