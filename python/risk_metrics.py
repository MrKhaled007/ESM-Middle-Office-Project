import pandas as pd
import numpy as np
import sqlite3

# ── Connect to database ────────────────────────────────────────────────────────
conn = sqlite3.connect("data/esm_database.db")

bonds      = pd.read_sql("SELECT * FROM bonds",      conn)
collateral = pd.read_sql("SELECT * FROM collateral", conn)
derivs     = pd.read_sql("SELECT * FROM derivatives", conn)

print("✅ Data loaded from database\n")
print("=" * 60)
print("RISK METRICS CALCULATION")
print("=" * 60)


# ══════════════════════════════════════════════════════════════════════════════
# METRIC 1 — DV01 (Interest Rate Sensitivity)
# ══════════════════════════════════════════════════════════════════════════════
# Formula:
#   DV01 = (Market Value × Modified Duration × 0.0001)
#
# Modified Duration approximation:
#   ModDur ≈ years_to_maturity / (1 + coupon_rate/100)
#
# Intuition: a 10-year bond with a 2% coupon is MORE sensitive to rate
# changes than a 2-year bond with a 5% coupon.

bonds["issue_date"]    = pd.to_datetime(bonds["issue_date"])
bonds["maturity_date"] = pd.to_datetime(bonds["maturity_date"])
today                  = pd.Timestamp.today()

bonds["years_to_maturity"] = (
    (bonds["maturity_date"] - today).dt.days / 365
).clip(lower=0)

bonds["modified_duration"] = (
    bonds["years_to_maturity"] / (1 + bonds["coupon_rate_pct"] / 100)
)

# DV01 per bond (in EUR)
bonds["dv01_EUR"] = (
    bonds["market_value_EUR"] * bonds["modified_duration"] * 0.0001
).round(2)

dv01_summary = (
    bonds.groupby("country")
    .agg(
        total_market_value_EUR = ("market_value_EUR", "sum"),
        avg_modified_duration  = ("modified_duration", "mean"),
        total_dv01_EUR         = ("dv01_EUR", "sum"),
    )
    .round(2)
    .sort_values("total_dv01_EUR", ascending=False)
    .reset_index()
)

# Portfolio-level total
portfolio_dv01 = bonds["dv01_EUR"].sum()

print("\n📊 METRIC 1 — DV01 by Country (EUR per 1bp rate move):")
print("-" * 60)
print(dv01_summary.to_string(index=False))
print(f"\n🔢 Total Portfolio DV01: EUR {portfolio_dv01:,.2f}")
print("   → If rates rise 0.01%, portfolio loses EUR"
      f" {portfolio_dv01:,.0f}")

dv01_summary.to_csv("data/metric1_dv01.csv", index=False)
print("✅ Saved to data/metric1_dv01.csv")


# ══════════════════════════════════════════════════════════════════════════════
# METRIC 2 — FX Exposure by Currency
# ══════════════════════════════════════════════════════════════════════════════
# Measures how much of the portfolio is exposed to currency fluctuation.
# EUR positions = no FX risk (home currency)
# USD / GBP positions = exposed to exchange rate moves

fx_exposure = (
    bonds.groupby("currency")
    .agg(
        num_bonds              = ("bond_id", "count"),
        total_market_value_EUR = ("market_value_EUR", "sum"),
    )
    .reset_index()
    .sort_values("total_market_value_EUR", ascending=False)
)

fx_exposure["share_pct"] = (
    fx_exposure["total_market_value_EUR"] /
    fx_exposure["total_market_value_EUR"].sum() * 100
).round(2)

# Non-EUR exposure total
non_eur = fx_exposure[fx_exposure["currency"] != "EUR"]["total_market_value_EUR"].sum()
total   = fx_exposure["total_market_value_EUR"].sum()

print("\n\n📊 METRIC 2 — FX Exposure by Currency:")
print("-" * 60)
print(fx_exposure.to_string(index=False))
print(f"\n🔢 Non-EUR Exposure: EUR {non_eur:,.0f}"
      f" ({non_eur/total*100:.1f}% of portfolio)")
print("   → This portion is exposed to USD/GBP exchange rate moves")

fx_exposure.to_csv("data/metric2_fx_exposure.csv", index=False)
print("✅ Saved to data/metric2_fx_exposure.csv")


# ══════════════════════════════════════════════════════════════════════════════
# METRIC 3 — Collateral Coverage Analysis
# ══════════════════════════════════════════════════════════════════════════════
# For each counterparty: are they adequately collateralized?
# Coverage < 100% = ESM is at risk if that counterparty defaults

coverage = (
    collateral.groupby("counterparty")
    .agg(
        total_collateral_EUR = ("collateral_value_EUR", "sum"),
        total_exposure_EUR   = ("exposure_EUR", "sum"),
        num_positions        = ("collateral_id", "count"),
        undercollat_count    = ("status", lambda x: (x == "Undercollateralized").sum()),
    )
    .reset_index()
)

coverage["coverage_ratio_pct"] = (
    coverage["total_collateral_EUR"] /
    coverage["total_exposure_EUR"] * 100
).round(2)

coverage["rag_status"] = coverage["coverage_ratio_pct"].apply(
    lambda x: "🔴 RED"    if x < 95  else
              "🟡 AMBER"  if x < 105 else
              "🟢 GREEN"
)

coverage = coverage.sort_values("coverage_ratio_pct").reset_index(drop=True)

print("\n\n📊 METRIC 3 — Collateral Coverage by Counterparty:")
print("-" * 60)
print(coverage[["counterparty", "total_collateral_EUR",
                "total_exposure_EUR", "coverage_ratio_pct",
                "rag_status"]].to_string(index=False))

red   = (coverage["rag_status"].str.contains("RED")).sum()
amber = (coverage["rag_status"].str.contains("AMBER")).sum()
green = (coverage["rag_status"].str.contains("GREEN")).sum()
print(f"\n🔢 Summary: 🔴 {red} RED  |  🟡 {amber} AMBER  |  🟢 {green} GREEN")

coverage.to_csv("data/metric3_collateral_coverage.csv", index=False)
print("✅ Saved to data/metric3_collateral_coverage.csv")


# ══════════════════════════════════════════════════════════════════════════════
# SAVE ENRICHED BONDS TABLE BACK TO DATABASE
# ══════════════════════════════════════════════════════════════════════════════
# We add the calculated columns (DV01, duration) back to the database
# so Power BI can use them directly

bonds.to_sql("bonds_enriched", conn, if_exists="replace", index=False)
coverage.to_sql("collateral_coverage", conn, if_exists="replace", index=False)
dv01_summary.to_sql("dv01_by_country", conn, if_exists="replace", index=False)
fx_exposure.to_sql("fx_exposure", conn, if_exists="replace", index=False)

conn.close()

print("\n" + "=" * 60)
print("✅ All risk metrics calculated and saved.")
print("   - data/metric1_dv01.csv")
print("   - data/metric2_fx_exposure.csv")
print("   - data/metric3_collateral_coverage.csv")
print("   - Database updated with enriched tables")
print("=" * 60)