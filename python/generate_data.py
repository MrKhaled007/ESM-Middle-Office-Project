import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)

# ── Output folder ──────────────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)

# ── 1. BONDS PORTFOLIO ─────────────────────────────────────────────────────────
# Simulates ESM holding sovereign and agency bonds across eurozone countries

countries      = ["Germany", "France", "Italy", "Spain", "Netherlands",
                  "Belgium", "Austria", "Portugal", "Finland", "Ireland"]
currencies     = ["EUR", "USD", "GBP"]
bond_types     = ["Sovereign", "Agency", "Supranational"]

n_bonds = 50
today   = datetime.today()

bonds = pd.DataFrame({
    "bond_id":        [f"BOND-{str(i).zfill(3)}" for i in range(1, n_bonds + 1)],
    "country":        np.random.choice(countries, n_bonds),
    "bond_type":      np.random.choice(bond_types, n_bonds),
    "currency":       np.random.choice(currencies, n_bonds, p=[0.70, 0.20, 0.10]),
    "face_value_EUR": np.random.randint(50, 500, n_bonds) * 1_000_000,
    "coupon_rate_pct": np.round(np.random.uniform(0.5, 5.5, n_bonds), 2),
    "issue_date":     [
        (today - timedelta(days=int(np.random.randint(180, 1800)))).strftime("%Y-%m-%d")
        for _ in range(n_bonds)
    ],
    "maturity_date":  [
        (today + timedelta(days=int(np.random.randint(365, 3650)))).strftime("%Y-%m-%d")
        for _ in range(n_bonds)
    ],
    "market_value_EUR": np.round(
        np.random.uniform(0.92, 1.08, n_bonds) * np.random.randint(50, 500, n_bonds) * 1_000_000, 2
    ),
    "credit_rating":  np.random.choice(["AAA", "AA+", "AA", "AA-", "A+", "A"], n_bonds),
})

bonds.to_csv("data/bonds_portfolio.csv", index=False)
print(f"✅ bonds_portfolio.csv — {len(bonds)} rows")


# ── 2. DERIVATIVES ─────────────────────────────────────────────────────────────
# Simulates interest rate swaps (IRS) and FX forwards used for hedging

counterparties  = ["Deutsche Bank", "BNP Paribas", "Societe Generale",
                   "Barclays", "JPMorgan", "Goldman Sachs", "HSBC", "UniCredit"]
deriv_types     = ["Interest Rate Swap", "FX Forward"]
fx_pairs        = ["EUR/USD", "EUR/GBP", "EUR/CHF", "EUR/JPY"]

n_derivs = 30

derivatives = pd.DataFrame({
    "deriv_id":         [f"DERIV-{str(i).zfill(3)}" for i in range(1, n_derivs + 1)],
    "type":             np.random.choice(deriv_types, n_derivs),
    "counterparty":     np.random.choice(counterparties, n_derivs),
    "notional_EUR":     np.random.randint(10, 200, n_derivs) * 1_000_000,
    "fx_pair":          np.random.choice(fx_pairs + [None], n_derivs, p=[0.15, 0.15, 0.10, 0.10, 0.50]),
    "fixed_rate_pct":   np.round(np.random.uniform(1.0, 4.5, n_derivs), 3),
    "floating_rate_pct":np.round(np.random.uniform(0.5, 4.0, n_derivs), 3),
    "start_date":       [
        (today - timedelta(days=int(np.random.randint(30, 720)))).strftime("%Y-%m-%d")
        for _ in range(n_derivs)
    ],
    "maturity_date":    [
        (today + timedelta(days=int(np.random.randint(90, 1800)))).strftime("%Y-%m-%d")
        for _ in range(n_derivs)
    ],
    "mtm_value_EUR":    np.round(np.random.uniform(-5_000_000, 8_000_000, n_derivs), 2),
    "status":           np.random.choice(["Active", "Active", "Active", "Matured"], n_derivs),
})

derivatives.to_csv("data/derivatives.csv", index=False)
print(f"✅ derivatives.csv     — {len(derivatives)} rows")


# ── 3. COLLATERAL ──────────────────────────────────────────────────────────────
# Simulates assets pledged by counterparties to cover their derivative exposure

collateral_types = ["Government Bond", "Cash (EUR)", "Cash (USD)", "Agency Bond", "T-Bill"]

n_collateral = 40

# Exposure per counterparty (sum of notionals from derivatives)
cp_exposure = (
    derivatives.groupby("counterparty")["notional_EUR"]
    .sum()
    .reset_index()
    .rename(columns={"notional_EUR": "exposure_EUR"})
)

rows = []
for i in range(n_collateral):
    cp   = np.random.choice(counterparties)
    exp  = float(cp_exposure.loc[cp_exposure["counterparty"] == cp, "exposure_EUR"].values[0]) \
           if cp in cp_exposure["counterparty"].values else np.random.randint(10, 100) * 1_000_000
    # Collateral value: sometimes over, sometimes under (realistic!)
    coll_val = round(exp * np.random.uniform(0.80, 1.20), 2)

    rows.append({
        "collateral_id":    f"COLL-{str(i+1).zfill(3)}",
        "counterparty":     cp,
        "collateral_type":  np.random.choice(collateral_types),
        "collateral_value_EUR": coll_val,
        "exposure_EUR":     round(exp, 2),
        "coverage_ratio":   round(coll_val / exp * 100, 2),
        "pledge_date":      (today - timedelta(days=int(np.random.randint(1, 365)))).strftime("%Y-%m-%d"),
        "status":           "Sufficient" if coll_val >= exp else "Undercollateralized",
    })

collateral = pd.DataFrame(rows)
collateral.to_csv("data/collateral.csv", index=False)
print(f"✅ collateral.csv      — {len(collateral)} rows")


# ── 4. RISK LIMITS ─────────────────────────────────────────────────────────────
# ESM sets max exposure limits per country — we track how close we are

limits = pd.DataFrame({
    "country":          countries,
    "limit_EUR":        [2_000_000_000, 1_800_000_000, 1_200_000_000, 1_000_000_000,
                         900_000_000,   800_000_000,   700_000_000,   600_000_000,
                         500_000_000,   400_000_000],
    "limit_type":       ["Sovereign Exposure"] * len(countries),
})

limits.to_csv("data/risk_limits.csv", index=False)
print(f"✅ risk_limits.csv     — {len(limits)} rows")

print("\n🎯 All 4 datasets saved to data/ folder.")