# FUTURE_DS_02 - Telco Customer Churn Analytics

**Future Interns - Data Science & Analytics, Task 2** | Telco Churn Analysis

## Business problem
A telecommunications provider seeks to understand the primary drivers of customer churn, quantify revenue loss, examine retention dynamics across customer lifetime, and identify high-risk customer segments to take targeted retention actions.

## Dataset
[Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) (Kaggle): 7,043 customers, 21 attributes covering demographics, account information, and subscribed services. Not owned by me; used for educational purposes.

## Dashboard
The analysis was designed around a 4-frame executive dashboard (Overview, Churn drivers, Customer lifetime, Action plan).
- Images directory (`images/`): No static PNG page mockups exist in the repository (the interactive UI was created and rendered directly via the Streamlit application and Figma Make web components).
- PDF report (`dashboard/FUTURE_DS_02_dashboard.pdf`): Currently pending compilation; exploratory and executive views are available live in the interactive application.

## Data cleaning
Summary of [`docs/cleaning_log.md`](docs/cleaning_log.md):
- Loaded raw dataset of 7,043 customer rows × 21 columns (`WA_Fn-UseC_-Telco-Customer-Churn.xls`).
- Standardised column headers into consistent lower snake_case.
- Handled `total_charges`: coerced 11 blank / whitespace strings to NaN (belonging to new customers with `tenure = 0` months) and filled them with `0.0`.
- Verified record uniqueness: 0 exact duplicate rows found; all 7,043 customer rows retained.
- Added helper features: binary `churn_flag` (1 = churned, 0 = retained), standardized `senior_citizen` ('Yes'/'No'), and binned `tenure_band` (0-6, 7-12, 13-24, 25-48, 49-72 months).

## Headline KPIs
Calculated directly from [`data/telco_clean.csv`](data/telco_clean.csv):

| Metric | Value | Detail |
| :--- | :--- | :--- |
| **Total Customers** | **7,043** | Full dataset baseline |
| **Churn Rate** | **26.5%** | 1,869 customers churned |
| **Monthly Revenue Lost to Churn** | **$139K** | $139,131 (30.5% of total $456,117 monthly revenue) |
| **Average Monthly Charge** | **$74.44** | Churned ($74.44) vs. retained ($61.27) |
| **Average Tenure** | **18.0 mos** | Churned (18.0 months) vs. retained (37.6 months) |

## Key insights
All findings reflect observed statistical associations, never proven causes:
1. **Contract type**: Churn rate is 42.7% for Month-to-month contracts, dropping sharply to 11.3% for One year, and 2.8% for Two year contracts.
2. **Early tenure vulnerability**: Customers in their first 6 months exhibit a 52.9% churn rate, compared to only 9.5% for customers with 49+ months tenure.
3. **Internet service tier**: Fiber optic subscribers churn at 41.9%, more than double the 19.0% churn rate observed among DSL subscribers.
4. **Payment method friction**: Customers paying via Electronic check show a 45.3% churn rate, vs. 15.2% to 19.1% across automated bank transfers, credit cards, and mailed checks.
5. **Technical support engagement**: Customers without Tech Support churn at 41.6%, compared to 15.2% for those with active tech support.
6. **Demographics**: Senior citizens show a 41.7% churn rate vs. 23.6% for non-seniors.
7. **Highest-risk segment**: The intersection of Month-to-month contract, Fiber optic internet, and Electronic check billing accounts for 1,307 customers, with a 60.4% churn rate, generating 42.2% of all churners company-wide.
8. **Survival milestones**: Kaplan-Meier survival curves show active customer retention at 12, 24, and 48 months:
   - *Month-to-month*: 70.3% (12 mo) → 58.6% (24 mo) → 39.7% (48 mo)
   - *One year*: 99.1% (12 mo) → 97.8% (24 mo) → 91.7% (48 mo)
   - *Two year*: 100.0% (12 mo) → 100.0% (24 mo) → 99.6% (48 mo)

## Recommendations
Ranked retention initiatives structured as empirical business tests:
1. **Incentivize annual contract migrations**: Test introducing introductory discounts (e.g., $5/month discount or free speed boost) for month-to-month customers switching to a 1-year contract, targeting the 42.7% vs. 11.3% churn gap.
2. **Launch structured first-6-months customer onboarding**: Test automated proactive check-ins at day 30, 60, and 90 with satisfaction surveys to curb the 52.9% initial 6-month attrition rate.
3. **Bundle tech support & online security with fiber subscriptions**: Test offering complimentary 6-month tech support bundles on high-tier fiber plans to reduce the 41.6% churn rate seen among unsupported users.
4. **Promote automated payment adoption**: Test offering a recurring bill credit ($2 to $5/month) for transitioning from electronic checks (45.3% churn) to automatic bank transfers or credit card auto-pay (15.2%–16.7% churn).
5. **Audit fiber optic pricing and service reliability**: Test targeted competitive retention offers and technical line health diagnostics for fiber optic accounts paying ~$74+/month to address the 41.9% fiber churn rate.

## Limitations
- **Observational associations, not proof of cause**: Features associated with higher retention (such as multi-year contracts or automatic payments) may reflect self-selection by inherently loyal customers rather than pure treatment effects. Fiber churn may reflect price sensitivity rather than network dissatisfaction.
- **Lack of temporal and geographical granularity**: The dataset does not include customer signup dates, regional geography, or verbatim customer exit survey responses; cohorts are reconstructed strictly from tenure intervals.
- **Tail estimate uncertainty**: Survival curves are less reliable at higher tenures where fewer than 100 customers remain at risk.
- **Cross-sectional snapshot**: The data represents a single point-in-time cross-section rather than a full multi-year panel tracking customer plan upgrades, downgrades, or price revisions over time.

## Interactive app

An interactive executive dashboard built with Streamlit and Plotly. Sidebar filters (Contract, Internet Service, Senior Citizen) update all KPIs, churn drivers, lifetime survival curves, cohort analysis, and action plan metrics in real time.

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Live app: https://futuer-data-science-02.streamlit.app

The app reads `data/telco_clean.csv` relative to its own location via `pathlib`, so it works from any working directory.

### Cohort view
The Customer lifetime tab features a tenure-based cohort view (`Cohort view: churn by plan and tenure`) analyzing churn rates across contract types (Month-to-month, One year, Two year) and tenure bands (0-6, 7-12, 13-24, 25-48, 49-72 months). Cells with fewer than 50 customers are flagged with an asterisk (`*`) for sample-size caution.

## Tools and AI disclosure
- **Core Tools**: Python 3.12 (pandas, NumPy, Matplotlib, Plotly, Streamlit).
- **AI Disclosure**: An AI assistant (Antigravity) was used to assist in authoring and reviewing the data pipelines, verification suites, and Streamlit dashboard code. All metrics, cohort aggregations, Kaplan-Meier computations, and findings were verified and validated against [`data/telco_clean.csv`](data/telco_clean.csv).

## How to reproduce
Run the pipeline scripts and verification suites from the repository root:

```bash
# 1. Environment setup
pip install -r requirements.txt

# 2. Data cleaning (reads raw data and produces data/telco_clean.csv)
python3 scripts/01_clean_telco.py

# 3. Tableau data export (generates customer, curve, cohort, and driver CSVs in data/tableau/)
python3 scripts/05_prepare_tableau_data.py

# 4. Run automated test suites
python3 scripts/04_check_app.py
python3 scripts/06_check_tableau_data.py

# 5. Launch interactive Streamlit application
streamlit run app/streamlit_app.py
```

## Repository structure
```
FUTURE_DS_02/
├── README.md                           # Project documentation, insights & reproduction guide
├── requirements.txt                    # Project dependencies (pandas, numpy, matplotlib, streamlit, plotly)
├── AGENTS.md                           # Repository rules & development instructions
├── CLAUDE.md                           # Operational guidelines
├── index.html                          # Web entrypoint shell
├── package.json                        # Node dependencies
├── pnpm-lock.yaml                      # Package lockfile
├── tsconfig.json                       # TypeScript configuration
├── vite.config.ts                      # Vite configuration
├── app/
│   └── streamlit_app.py                # 4-frame interactive executive Streamlit dashboard
├── dashboard/                          # Dashboard export directory
├── data/
│   ├── WA_Fn-UseC_-Telco-Customer-Churn.xls  # Raw customer churn dataset
│   ├── telco_clean.csv                 # Cleaned dataset (7,043 rows x 24 columns)
│   └── tableau/
│       ├── churn_drivers.csv           # Factor-level churn rates
│       ├── cohort_contract_tenure.csv  # Contract x Tenure band cohort matrix
│       ├── retention_curve.csv         # Kaplan-Meier survival curve data (0-72 months)
│       └── telco_customers_tableau.csv # Customer-level analytical file (30 columns)
├── design/                             # UI design asset directory
├── docs/
│   ├── cleaning_log.md                 # Data cleaning log & step-by-step audit
│   └── tableau_data_dictionary.md      # Field definitions & Tableau implementation notes
├── public/
│   ├── .gitattributes
│   └── favicon.png
├── scripts/
│   ├── 01_clean_telco.py               # Data cleaning & feature engineering script
│   ├── 04_check_app.py                 # Streamlit UI & mathematical validation suite (22 checks)
│   ├── 05_prepare_tableau_data.py      # Tableau-ready export preparation pipeline
│   └── 06_check_tableau_data.py        # Tableau dataset integrity verification suite (70 checks)
└── src/
    ├── App.tsx                         # Canonical React design mockup component
    ├── index.css                       # Design tokens, typography & component styling
    ├── main.tsx                        # Frontend mounting entrypoint
    └── vite-env.d.ts                   # Environment type declarations
```
