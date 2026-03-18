import pandas as pd
import sqlite3
import os

# ── Connect to SQLite database (creates the file if it doesn't exist) ──────────
db_path = "data/esm_database.db"
conn    = sqlite3.connect(db_path)
print(f"✅ Connected to database: {db_path}\n")

# ── Load all 4 CSVs into the database as tables ────────────────────────────────
tables = {
    "bonds":       "data/bonds_portfolio.csv",
    "derivatives": "data/derivatives.csv",
    "collateral":  "data/collateral.csv",
    "risk_limits": "data/risk_limits.csv",
}

for table_name, csv_path in tables.items():
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"✅ Loaded '{table_name}' table — {len(df)} rows")

print("\n" + "="*60)
print("RUNNING MIDDLE OFFICE SQL QUERIES")
print("="*60)


# ── QUERY 1: Total portfolio exposure per country ──────────────────────────────
# WHY: The Head of Division asks every morning — where is our money?

q1 = """
SELECT
    country,
    COUNT(bond_id)                          AS num_bonds,
    ROUND(SUM(face_value_EUR) / 1e6, 2)    AS total_face_value_MEUR,
    ROUND(SUM(market_value_EUR) / 1e6, 2)  AS total_market_value_MEUR,
    ROUND(AVG(coupon_rate_pct), 2)          AS avg_coupon_pct
FROM bonds
GROUP BY country
ORDER BY total_market_value_MEUR DESC;
"""

print("\n📊 QUERY 1 — Portfolio Exposure by Country (in Million EUR):")
print("-" * 60)
df_q1 = pd.read_sql(q1, conn)
print(df_q1.to_string(index=False))
df_q1.to_csv("data/query1_exposure_by_country.csv", index=False)


# ── QUERY 2: Collateral coverage — who is undercollateralized? ─────────────────
# WHY: Risk Management needs to know if any counterparty hasn't pledged enough

q2 = """
SELECT
    counterparty,
    COUNT(collateral_id)                        AS num_positions,
    ROUND(SUM(collateral_value_EUR) / 1e6, 2)  AS total_collateral_MEUR,
    ROUND(SUM(exposure_EUR) / 1e6, 2)          AS total_exposure_MEUR,
    ROUND(SUM(collateral_value_EUR) /
          SUM(exposure_EUR) * 100, 2)           AS overall_coverage_ratio_pct,
    SUM(CASE WHEN status = 'Undercollateralized'
             THEN 1 ELSE 0 END)                 AS undercollateralized_count
FROM collateral
GROUP BY counterparty
ORDER BY overall_coverage_ratio_pct ASC;
"""

print("\n📊 QUERY 2 — Collateral Coverage by Counterparty:")
print("-" * 60)
df_q2 = pd.read_sql(q2, conn)
print(df_q2.to_string(index=False))
df_q2.to_csv("data/query2_collateral_coverage.csv", index=False)


# ── QUERY 3: Risk limit utilisation per country ────────────────────────────────
# WHY: Compliance checks — are we staying within approved exposure limits?

q3 = """
SELECT
    b.country,
    ROUND(SUM(b.market_value_EUR) / 1e6, 2)    AS current_exposure_MEUR,
    ROUND(r.limit_EUR / 1e6, 2)                AS limit_MEUR,
    ROUND(SUM(b.market_value_EUR) /
          r.limit_EUR * 100, 2)                 AS utilisation_pct,
    CASE
        WHEN SUM(b.market_value_EUR) / r.limit_EUR * 100 >= 90 THEN 'RED'
        WHEN SUM(b.market_value_EUR) / r.limit_EUR * 100 >= 70 THEN 'AMBER'
        ELSE 'GREEN'
    END AS rag_status
FROM bonds b
JOIN risk_limits r ON b.country = r.country
GROUP BY b.country
ORDER BY utilisation_pct DESC;
"""

print("\n📊 QUERY 3 — Risk Limit Utilisation (RAG Status):")
print("-" * 60)
df_q3 = pd.read_sql(q3, conn)
print(df_q3.to_string(index=False))
df_q3.to_csv("data/query3_limit_utilisation.csv", index=False)


# ── QUERY 4: Active derivatives summary by counterparty ───────────────────────
# WHY: Front Office needs a daily snapshot of live derivative positions

q4 = """
SELECT
    counterparty,
    type                                        AS instrument_type,
    COUNT(deriv_id)                             AS num_contracts,
    ROUND(SUM(notional_EUR) / 1e6, 2)          AS total_notional_MEUR,
    ROUND(SUM(mtm_value_EUR) / 1e6, 4)         AS total_mtm_MEUR
FROM derivatives
WHERE status = 'Active'
GROUP BY counterparty, type
ORDER BY total_notional_MEUR DESC;
"""

print("\n📊 QUERY 4 — Active Derivatives by Counterparty:")
print("-" * 60)
df_q4 = pd.read_sql(q4, conn)
print(df_q4.to_string(index=False))
df_q4.to_csv("data/query4_derivatives_summary.csv", index=False)


# ── Done ───────────────────────────────────────────────────────────────────────
conn.close()
print("\n" + "="*60)
print("✅ Database created and all queries saved to data/ folder.")
print("="*60)