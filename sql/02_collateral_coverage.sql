-- Collateral coverage ratio per counterparty
SELECT
    counterparty,
    ROUND(SUM(collateral_value_EUR) / 1e6, 2)      AS total_collateral_MEUR,
    ROUND(SUM(exposure_EUR) / 1e6, 2)              AS total_exposure_MEUR,
    ROUND(SUM(collateral_value_EUR) /
          SUM(exposure_EUR) * 100, 2)               AS coverage_ratio_pct,
    SUM(CASE WHEN status = 'Undercollateralized'
             THEN 1 ELSE 0 END)                     AS undercollateralized_count
FROM collateral
GROUP BY counterparty
ORDER BY coverage_ratio_pct ASC;