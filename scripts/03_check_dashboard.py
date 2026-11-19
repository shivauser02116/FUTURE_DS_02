#!/usr/bin/env python3
"""
scripts/03_check_dashboard.py
=============================
Automated test suite verifying the dashboard output artifacts and calculations:
  - Customers: 7,043
  - Churned: 1,869
  - Churn rate: 26.5%
  - Contract churn: Month-to-month 42.7%, One year 11.3%, Two year 2.8%
  - Tenure bands churn: 0-6 52.9%, 7-12 35.9%, 13-24 28.7%, 25-48 20.4%, 49-72 9.5%
  - Retention 12/24/48 for:
      * Month-to-month: 0.703, 0.586, 0.397
      * One year: 0.991, 0.978, 0.917
      * Two year: 1.000, 1.000, 0.996
  - High-risk segment: 1,307 customers, 60.4%, 42.2%
  - Cohort cells Month-to-month: 55.2%, 42.0%, 37.7%, 32.9%, 26.0%
  - File existence: dashboard/FUTURE_DS_02_dashboard.pdf, images/page_1.png..page_4.png

Usage:
    python3 scripts/03_check_dashboard.py
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "telco_clean.csv"
DASHBOARD_PDF = REPO_ROOT / "dashboard" / "FUTURE_DS_02_dashboard.pdf"
IMAGES_DIR = REPO_ROOT / "images"

passed_count = 0
failed_count = 0


def report(name: str, passed: bool, actual_str: str):
    global passed_count, failed_count
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: {actual_str}")
    if passed:
        passed_count += 1
    else:
        failed_count += 1


print("=" * 70)
print("  FUTURE_DS_02: STATIC DASHBOARD VERIFICATION SUITE")
print("=" * 70)

# ---------------------------------------------------------------------------
# Section 1: Output Artifact Existence Checks
# ---------------------------------------------------------------------------
print("\n--- Section 1: Dashboard Artifacts Existence ---")

try:
    exists = DASHBOARD_PDF.is_file() and DASHBOARD_PDF.stat().st_size > 1000
    report(
        "PDF artifact exists (FUTURE_DS_02_dashboard.pdf)",
        exists,
        f"{DASHBOARD_PDF.stat().st_size / 1024:.1f} KB" if exists else "Missing/Empty",
    )
except Exception as e:
    report("PDF artifact exists", False, f"Error: {e}")

for page_num in range(1, 5):
    try:
        img_path = IMAGES_DIR / f"page_{page_num}.png"
        exists = img_path.is_file() and img_path.stat().st_size > 1000
        report(
            f"Image artifact exists (page_{page_num}.png)",
            exists,
            f"{img_path.stat().st_size / 1024:.1f} KB" if exists else "Missing/Empty",
        )
    except Exception as e:
        report(f"Image artifact exists (page_{page_num}.png)", False, f"Error: {e}")

# ---------------------------------------------------------------------------
# Section 2: Core Dataset KPI Checks
# ---------------------------------------------------------------------------
print("\n--- Section 2: Core Dataset KPI Checks ---")

df = None
try:
    df = pd.read_csv(DATA_PATH)
    report("Dataset loaded successfully", True, f"{len(df):,} rows from {DATA_PATH.name}")
except Exception as e:
    report("Dataset loaded successfully", False, f"Error: {e}")
    sys.exit(1)

try:
    total_cust = len(df)
    report("Total customers == 7,043", total_cust == 7043, f"{total_cust:,}")
except Exception as e:
    report("Total customers == 7,043", False, f"Error: {e}")

try:
    churned_cust = int(df["churn_flag"].sum())
    report("Churned customers == 1,869", churned_cust == 1869, f"{churned_cust:,}")
except Exception as e:
    report("Churned customers == 1,869", False, f"Error: {e}")

try:
    churn_rate = churned_cust / total_cust * 100
    report("Churn rate == 26.5%", abs(churn_rate - 26.5) <= 0.1, f"{churn_rate:.1f}%")
except Exception as e:
    report("Churn rate == 26.5%", False, f"Error: {e}")

# ---------------------------------------------------------------------------
# Section 3: Contract Churn Rates (42.7 / 11.3 / 2.8%)
# ---------------------------------------------------------------------------
print("\n--- Section 3: Contract Churn Rate Checks ---")

expected_contracts = [
    ("Month-to-month", 42.7),
    ("One year", 11.3),
    ("Two year", 2.8),
]

for c_name, exp_rate in expected_contracts:
    try:
        sub = df[df["contract"] == c_name]
        act_rate = sub["churn_flag"].mean() * 100
        report(
            f"Contract '{c_name}' churn rate ({exp_rate}%)",
            abs(act_rate - exp_rate) <= 0.15,
            f"{act_rate:.1f}% (n={len(sub):,})",
        )
    except Exception as e:
        report(f"Contract '{c_name}' churn rate", False, f"Error: {e}")

# ---------------------------------------------------------------------------
# Section 4: Tenure Band Churn Rates (52.9 / 35.9 / 28.7 / 20.4 / 9.5%)
# ---------------------------------------------------------------------------
print("\n--- Section 4: Tenure Band Churn Rate Checks ---")


def get_tb(t):
    if t <= 6:
        return "0-6"
    elif t <= 12:
        return "7-12"
    elif t <= 24:
        return "13-24"
    elif t <= 48:
        return "25-48"
    else:
        return "49-72"


df["tb_calc"] = df["tenure"].map(get_tb)

expected_tenure_bands = [
    ("0-6", 52.9),
    ("7-12", 35.9),
    ("13-24", 28.7),
    ("25-48", 20.4),
    ("49-72", 9.5),
]

for tb_name, exp_rate in expected_tenure_bands:
    try:
        sub = df[df["tb_calc"] == tb_name]
        act_rate = sub["churn_flag"].mean() * 100
        report(
            f"Tenure band '{tb_name}' churn rate ({exp_rate}%)",
            abs(act_rate - exp_rate) <= 0.15,
            f"{act_rate:.1f}% (n={len(sub):,})",
        )
    except Exception as e:
        report(f"Tenure band '{tb_name}' churn rate", False, f"Error: {e}")

# ---------------------------------------------------------------------------
# Section 5: Kaplan-Meier Retention (12, 24, 48 months)
# ---------------------------------------------------------------------------
print("\n--- Section 5: Kaplan-Meier Retention Rate Checks ---")

km_df = df[df["tenure"] > 0]
expected_km = {
    "Month-to-month": {12: 0.703, 24: 0.586, 48: 0.397},
    "One year": {12: 0.991, 24: 0.978, 48: 0.917},
    "Two year": {12: 1.000, 24: 1.000, 48: 0.996},
}

for c_name, milestones in expected_km.items():
    try:
        sub = km_df[km_df["contract"] == c_name]
        S = 1.0
        ret_map = {}
        for t in range(1, 73):
            at_risk = int((sub["tenure"] >= t).sum())
            if at_risk < 100:
                break
            events = int(((sub["tenure"] == t) & (sub["churn_flag"] == 1)).sum())
            S *= 1.0 - (events / at_risk if at_risk > 0 else 0.0)
            if t in milestones:
                ret_map[t] = S

        for m, exp_val in milestones.items():
            act_val = ret_map.get(m, 0.0)
            report(
                f"KM '{c_name}' retention @ month {m} ({exp_val:.3f})",
                abs(act_val - exp_val) <= 0.005,
                f"{act_val:.3f}",
            )
    except Exception as e:
        report(f"KM '{c_name}' retention", False, f"Error: {e}")

# ---------------------------------------------------------------------------
# Section 6: Highest-Risk Segment (1,307 cust, 60.4% churn, 42.2% share)
# ---------------------------------------------------------------------------
print("\n--- Section 6: Highest-Risk Segment Checks ---")

try:
    risk_mask = (
        (df["contract"] == "Month-to-month")
        & (df["internet_service"] == "Fiber optic")
        & (df["payment_method"] == "Electronic check")
    )
    risk_df = df[risk_mask]
    risk_cnt = len(risk_df)
    risk_churn = int(risk_df["churn_flag"].sum())
    risk_rate = risk_churn / risk_cnt * 100
    risk_share = risk_churn / churned_cust * 100

    report(
        "High-risk segment customer count == 1,307",
        risk_cnt == 1307,
        f"{risk_cnt:,}",
    )
    report(
        "High-risk segment churn rate == 60.4%",
        abs(risk_rate - 60.4) <= 0.15,
        f"{risk_rate:.1f}%",
    )
    report(
        "High-risk segment share of all churners == 42.2%",
        abs(risk_share - 42.2) <= 0.15,
        f"{risk_share:.1f}%",
    )
except Exception as e:
    report("Highest-risk segment checks", False, f"Error: {e}")

# ---------------------------------------------------------------------------
# Section 7: Month-to-Month Cohort Cells (55.2 / 42.0 / 37.7 / 32.9 / 26.0%)
# ---------------------------------------------------------------------------
print("\n--- Section 7: Month-to-Month Cohort Cell Checks ---")

m2m_df = df[df["contract"] == "Month-to-month"]
expected_m2m_cohorts = [
    ("0-6", 55.2),
    ("7-12", 42.0),
    ("13-24", 37.7),
    ("25-48", 32.9),
    ("49-72", 26.0),
]

for tb_name, exp_rate in expected_m2m_cohorts:
    try:
        sub = m2m_df[m2m_df["tb_calc"] == tb_name]
        act_rate = sub["churn_flag"].mean() * 100
        report(
            f"M2M Cohort cell '{tb_name}' churn rate ({exp_rate}%)",
            abs(act_rate - exp_rate) <= 0.15,
            f"{act_rate:.1f}% (n={len(sub):,})",
        )
    except Exception as e:
        report(f"M2M Cohort cell '{tb_name}' churn rate", False, f"Error: {e}")

# ---------------------------------------------------------------------------
# Final Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
total_tests = passed_count + failed_count
print(f"  TOTAL CHECKS: {total_tests} | PASSED: {passed_count} | FAILED: {failed_count}")
print("=" * 70)

if failed_count > 0:
    print(f"\n❌ Dashboard verification failed with {failed_count} failing check(s).")
    sys.exit(1)
else:
    print("\n✅ All static dashboard verification checks passed successfully!")
    sys.exit(0)
