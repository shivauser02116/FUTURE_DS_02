# FUTURE_DS_02 - Telco Customer Churn Analytics

**Future Interns - Data Science & Analytics, Task 2** | Telco Churn Analysis

## Business problem
A telecommunications provider seeks to understand the primary drivers of customer churn, quantify revenue loss, examine retention dynamics across customer lifetime, and identify high-risk customer segments to take targeted retention actions.

## Dataset
[Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) (Kaggle): 7,043 customers, 21 attributes covering demographics, account information, and subscribed services.

## Interactive app

An interactive executive dashboard built with Streamlit and Plotly. Sidebar filters (Contract, Internet Service, Senior Citizen) update all KPIs, churn drivers, lifetime survival curves, cohort analysis, and action plan metrics in real time.

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Live app: (add link after deploying)

The app reads `data/telco_clean.csv` relative to its own location via `pathlib`, so it works from any working directory.

### Cohort view
The Customer lifetime tab features a tenure-based cohort view (`Cohort view: churn by plan and tenure`) analyzing churn rates across contract types (Month-to-month, One year, Two year) and tenure bands (0-6, 7-12, 13-24, 25-48, 49-72 months). Cells with fewer than 50 customers are flagged with an asterisk for sample-size caution.
