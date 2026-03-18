# ESM Middle Office — Investment & Risk Dashboard

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Power BI](https://img.shields.io/badge/PowerBI-Dashboard-yellow?logo=powerbi)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey?logo=sqlite)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

A full-stack Middle Office data analytics project simulating the investment monitoring,
collateral management, and risk limit tracking workflows of a European financial institution
— modelled on the operational structure of the European Stability Mechanism (ESM).

---

## 📌 Business Context

The **European Stability Mechanism (ESM)** is the permanent crisis resolution fund for
eurozone countries. It manages a multi-billion euro portfolio of bonds and derivatives,
monitors counterparty collateral on a daily basis, and enforces strict country-level
exposure limits to manage sovereign risk.

The **Middle Office** sits between the Front Office (trading) and Back Office (settlement).
Its core responsibilities are:

- Maintaining accurate databases of investment and funding transactions
- Reconciling collateral positions with counterparties daily
- Monitoring risk limit utilisation and flagging breaches to senior management
- Reporting investment activity and performance to the Management Board

This project replicates those workflows end-to-end using Python, SQL, and Power BI.

---

## 🗂️ Project Structure

```
esm-middle-office-dashboard/
│
├── data/                          # All datasets (generated + query outputs)
│   ├── bonds_portfolio.csv        # 50 simulated bond holdings
│   ├── derivatives.csv            # 30 interest rate swaps & FX forwards
│   ├── collateral.csv             # 40 collateral positions
│   ├── risk_limits.csv            # Country-level exposure limits
│   ├── esm_database.db            # SQLite database (all tables)
│   ├── query1_exposure_by_country.csv
│   ├── query2_collateral_coverage.csv
│   ├── query3_limit_utilisation.csv
│   ├── query4_derivatives_summary.csv
│   ├── metric1_dv01.csv
│   ├── metric2_fx_exposure.csv
│   └── metric3_collateral_coverage.csv
│
├── python/
│   ├── generate_data.py           # Simulates realistic Middle Office datasets
│   ├── load_to_sqlite.py          # Loads data into SQLite, runs SQL queries
│   └── risk_metrics.py            # Calculates DV01, FX exposure, coverage ratios
│
├── sql/                           # SQL queries (also embedded in load_to_sqlite.py)
│
├── powerbi/
│   ├── ESM_Dashboard.pbix         # Full 3-page Power BI report
│   └── ESM_Theme.json             # Custom dark navy theme file
│
└── README.md
```

---

## ⚙️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Data generation, risk metric calculations |
| Pandas / NumPy | Data manipulation and financial math |
| SQLite | Relational database for all Middle Office tables |
| SQL | Aggregation queries for exposure, collateral, limits |
| Power BI Desktop | Interactive dashboards and RAG reporting |
| DAX | Custom measures for coverage ratios and utilisation % |

---

## 📊 The Three Dashboards

### 1 — Investment Activity & Portfolio Overview
Answers: *Where is our money invested and what does the portfolio look like?*

- KPI cards: Total portfolio value, bond count, average coupon, portfolio DV01
- Bar chart: Market value by country (sorted descending)
- Donut charts: Portfolio split by bond type and by currency (FX exposure)
- Table: Full bond holdings sorted by market value

### 2 — Collateral Reconciliation
Answers: *Are all counterparties adequately collateralized? Where are we at risk?*

- KPI cards: Total collateral, total exposure, position count, undercollateralized count
- Bar chart: Coverage ratio % per counterparty with 100% minimum reference line
- Clustered column chart: Collateral pledged vs exposure side by side
- RAG status table: Full counterparty list with RED/AMBER/GREEN conditional formatting
- Donut chart: Collateral breakdown by asset type

### 3 — Risk Limit Monitoring
Answers: *Are we breaching any approved country exposure limits?*

- KPI cards: Total exposure, total limits, average utilisation, breached limits count
- Bar chart: Limit utilisation % per country with 70% (amber) and 90% (red) reference lines
- Clustered column chart: Current exposure vs approved limit per country
- Full limit report table with RAG conditional formatting
- DV01 bar chart: Interest rate sensitivity per country

---

## 🧮 Risk Metrics Explained

### DV01 (Dollar Value of 01)
Measures how much the portfolio loses in EUR if interest rates rise by 1 basis point (0.01%).

```
DV01 = Market Value × Modified Duration × 0.0001
Modified Duration ≈ Years to Maturity / (1 + Coupon Rate)
```

A high DV01 on a country means that country's bonds are highly sensitive to rate moves —
important for the ESM which holds long-dated sovereign debt.

### FX Exposure
Measures what proportion of the portfolio is denominated in non-EUR currencies (USD, GBP).
These positions are exposed to exchange rate fluctuations and may require hedging via
FX forwards — which are included in the derivatives dataset.

### Collateral Coverage Ratio
```
Coverage Ratio = (Collateral Value / Exposure) × 100
```
- **≥ 105%** → GREEN — fully covered with buffer
- **95–105%** → AMBER — adequate but close to minimum
- **< 95%** → RED — undercollateralized, action required

---

## 🚀 How to Run

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/esm-middle-office-dashboard.git
cd esm-middle-office-dashboard
```

**2. Install dependencies**
```bash
pip install pandas numpy
```

**3. Generate the data**
```bash
python python/generate_data.py
```

**4. Load into database and run SQL queries**
```bash
python python/load_to_sqlite.py
```

**5. Calculate risk metrics**
```bash
python python/risk_metrics.py
```

**6. Open the Power BI dashboard**
- Open `powerbi/ESM_Dashboard.pbix` in Power BI Desktop
- Refresh the data source if prompted

---

## 💡 Key Design Decisions

**Why SQLite?**
In production, Middle Office data lives in enterprise databases (Oracle, SQL Server).
SQLite replicates that relational structure without infrastructure overhead —
demonstrating the same SQL skills in a portable format.

**Why simulate undercollateralized positions?**
Real collateral books always have positions requiring remediation. A dashboard that
only shows green would not reflect reality or demonstrate genuine understanding of
collateral risk management.

**Why DV01 and not just duration?**
DV01 translates duration into a concrete EUR figure — the language risk managers
and the Management Board actually use when discussing interest rate sensitivity.

---

## 👤 Author

**Mohammed Khaled**
Final-year BSc Data Science, Protection & Security — Thomas More University, Mechelen
Internship: Agiliz (Power BI, Python, Machine Learning)

📧 khaledalam893@email.com
🔗 [LinkedIn]([https://linkedin.com/in/yourprofile](https://www.linkedin.com/in/mohammed-khaled-43a220183/))
🐙 [GitHub](https://github.com/MrKhaled007)
