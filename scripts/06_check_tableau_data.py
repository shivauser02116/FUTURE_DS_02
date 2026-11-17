"""
scripts/06_check_tableau_data.py
================================
Automated test suite verifying the Tableau-ready data files in data/tableau/:
  - telco_customers_tableau.csv
  - retention_curve.csv
  - cohort_contract_tenure.csv
  - churn_drivers.csv

Usage:
    python3 scripts/06_check_tableau_data.py
"""

import sys
from pathlib import Path
import pandas as pd

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
TABLEAU_DIR = REPO_ROOT / "data" / "tableau"

# Tolerances specified:
# rates +/-0.2 points, dollars +/-0.5%, retention +/-0.005
RATE_TOL = 0.2001
DOLLAR_TOL = 0.005001
RET_TOL = 0.005001

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
print("  TABLEAU DATA VERIFICATION SUITE")
print("=" * 70)

# ===========================================================================
# 1. Customers File Checks
# ===========================================================================
print("\n--- 1. telco_customers_tableau.csv Checks ---")

df_cust = None
cust_path = TABLEAU_DIR / "telco_customers_tableau.csv"

try:
    df_cust = pd.read_csv(cust_path)
    report(
        "Customers file: 7,043 rows",
        len(df_cust) == 7043,
        f"{len(df_cust)} rows",
    )
except Exception as e:
    report("Customers file: 7,043 rows", False, f"Error: {e}")

try:
    uniq = df_cust["customer_id"].nunique() == 7043
    report(
        "Customers file: unique customer_id",
        uniq,
        f"{df_cust['customer_id'].nunique()} unique IDs",
    )
except Exception as e:
    report("Customers file: unique customer_id", False, f"Error: {e}")

try:
    # No empty cells
    null_counts = df_cust.isna().sum().sum()
    empty_strings = (df_cust.astype(str) == "").sum().sum()
    no_empty = (null_counts == 0) and (empty_strings == 0)
    report(
        "Customers file: no empty cells",
        no_empty,
        f"nulls={null_counts}, empty_strings={empty_strings}",
    )
except Exception as e:
    report("Customers file: no empty cells", False, f"Error: {e}")

try:
    s_count = int(df_cust["customer_count"].sum())
    report(
        "Customers file: sum(customer_count)=7,043",
        s_count == 7043,
        f"sum={s_count}",
    )
except Exception as e:
    report("Customers file: sum(customer_count)=7,043", False, f"Error: {e}")

try:
    churned_n = int(df_cust["churn_flag"].sum())
    report(
        "Customers file: churned 1,869",
        churned_n == 1869,
        f"churned={churned_n}",
    )
except Exception as e:
    report("Customers file: churned 1,869", False, f"Error: {e}")

try:
    c_rate = (df_cust["churn_flag"].sum() / len(df_cust)) * 100
    report(
        "Customers file: churn rate 26.5%",
        abs(c_rate - 26.5) <= RATE_TOL,
        f"rate={c_rate:.2f}%",
    )
except Exception as e:
    report("Customers file: churn rate 26.5%", False, f"Error: {e}")

try:
    tot_mc = float(df_cust["monthly_charges"].sum())
    diff_mc = abs(tot_mc - 456117) / 456117
    report(
        "Customers file: sum(monthly_charges)=$456,117",
        diff_mc <= DOLLAR_TOL,
        f"${tot_mc:,.2f} (diff {diff_mc:.4%})",
    )
except Exception as e:
    report("Customers file: sum(monthly_charges)=$456,117", False, f"Error: {e}")

try:
    tot_churn_rev = float(df_cust["churned_monthly_revenue"].sum())
    diff_cr = abs(tot_churn_rev - 139131) / 139131
    report(
        "Customers file: sum(churned_monthly_revenue)=$139,131",
        diff_cr <= DOLLAR_TOL,
        f"${tot_churn_rev:,.2f} (diff {diff_cr:.4%})",
    )
except Exception as e:
    report("Customers file: sum(churned_monthly_revenue)=$139,131", False, f"Error: {e}")

# ===========================================================================
# 2. High Risk Segment Checks
# ===========================================================================
print("\n--- 2. High Risk Segment Checks ---")

try:
    hrs = df_cust[df_cust["high_risk_segment"] == "Yes"]
    hrs_n = len(hrs)
    report(
        "High risk segment: 1,307 customers",
        hrs_n == 1307,
        f"customers={hrs_n}",
    )
except Exception as e:
    report("High risk segment: 1,307 customers", False, f"Error: {e}")

try:
    hrs_cr = (hrs["churn_flag"].sum() / len(hrs)) * 100
    report(
        "High risk segment: 60.4% churn",
        abs(hrs_cr - 60.4) <= RATE_TOL,
        f"churn_rate={hrs_cr:.2f}%",
    )
except Exception as e:
    report("High risk segment: 60.4% churn", False, f"Error: {e}")

try:
    tot_churners = df_cust["churn_flag"].sum()
    hrs_share = (hrs["churn_flag"].sum() / tot_churners) * 100
    report(
        "High risk segment: 42.2% of all churners",
        abs(hrs_share - 42.2) <= RATE_TOL,
        f"share={hrs_share:.2f}%",
    )
except Exception as e:
    report("High risk segment: 42.2% of all churners", False, f"Error: {e}")

# ===========================================================================
# 3. Churn Rate by Contract Checks
# ===========================================================================
print("\n--- 3. Churn Rate by Contract Checks ---")

try:
    contract_rates = (
        df_cust.groupby("contract")["churn_flag"].mean() * 100
    ).to_dict()
    m2m = contract_rates.get("Month-to-month", 0.0)
    report(
        "Contract: Month-to-month 42.7%",
        abs(m2m - 42.7) <= RATE_TOL,
        f"{m2m:.2f}%",
    )
except Exception as e:
    report("Contract: Month-to-month 42.7%", False, f"Error: {e}")

try:
    oy = contract_rates.get("One year", 0.0)
    report(
        "Contract: One year 11.3%",
        abs(oy - 11.3) <= RATE_TOL,
        f"{oy:.2f}%",
    )
except Exception as e:
    report("Contract: One year 11.3%", False, f"Error: {e}")

try:
    ty = contract_rates.get("Two year", 0.0)
    report(
        "Contract: Two year 2.8%",
        abs(ty - 2.8) <= RATE_TOL,
        f"{ty:.2f}%",
    )
except Exception as e:
    report("Contract: Two year 2.8%", False, f"Error: {e}")

# ===========================================================================
# 4. Churn Rate by Tenure Band Checks
# ===========================================================================
print("\n--- 4. Churn Rate by Tenure Band Checks ---")

try:
    tb_rates = (
        df_cust.groupby("tenure_band")["churn_flag"].mean() * 100
    ).to_dict()
    exp_tb = [("0-6", 52.9), ("7-12", 35.9), ("13-24", 28.7), ("25-48", 20.4), ("49-72", 9.5)]
    for band_label, exp_val in exp_tb:
        act_val = tb_rates.get(band_label, 0.0)
        report(
            f"Tenure band {band_label}: {exp_val}%",
            abs(act_val - exp_val) <= RATE_TOL,
            f"{act_val:.2f}%",
        )
except Exception as e:
    report("Churn rate by tenure_band", False, f"Error: {e}")

# ===========================================================================
# 5. Retention Curve Checks
# ===========================================================================
print("\n--- 5. retention_curve.csv Checks ---")

df_ret = None
ret_path = TABLEAU_DIR / "retention_curve.csv"

try:
    df_ret = pd.read_csv(ret_path)
    exp_km = {
        "Overall": {12: 0.843, 24: 0.789, 48: 0.709},
        "Month-to-month": {12: 0.703, 24: 0.586, 48: 0.397},
        "One year": {12: 0.991, 24: 0.978, 48: 0.917},
        "Two year": {12: 1.000, 24: 1.000, 48: 0.996},
        "Fiber optic": {12: 0.784, 24: 0.702, 48: 0.581},
        "DSL": {12: 0.868, 24: 0.831, 48: 0.785},
    }

    for seg_name, months in exp_km.items():
        sub_ret = df_ret[df_ret["segment"] == seg_name].set_index("month")
        for m, exp_val in months.items():
            if m in sub_ret.index:
                act_pct = sub_ret.loc[m, "retention_pct"]
                act_val = act_pct / 100.0
                report(
                    f"Retention curve: {seg_name} @ month {m} ({exp_val:.3f})",
                    abs(act_val - exp_val) <= RET_TOL,
                    f"{act_val:.3f} (pct={act_pct}%)",
                )
            else:
                report(f"Retention curve: {seg_name} @ month {m}", False, "Month not found")
except Exception as e:
    report("Retention curve checks", False, f"Error: {e}")

# ===========================================================================
# 6. Cohort Table Checks
# ===========================================================================
print("\n--- 6. cohort_contract_tenure.csv Checks ---")

df_cohort = None
cohort_path = TABLEAU_DIR / "cohort_contract_tenure.csv"

try:
    df_cohort = pd.read_csv(cohort_path)

    # Expected rates per contract
    exp_cohorts = {
        "Month-to-month": [("0-6", 55.2), ("7-12", 42.0), ("13-24", 37.7), ("25-48", 32.9), ("49-72", 26.0)],
        "One year": [("0-6", 10.3), ("7-12", 10.6), ("13-24", 8.1), ("25-48", 10.6), ("49-72", 12.9)],
        "Two year": [("0-6", 0.0), ("7-12", 0.0), ("13-24", 0.0), ("25-48", 2.2), ("49-72", 3.3)],
    }

    for c_name, bands_exp in exp_cohorts.items():
        for b_name, exp_r in bands_exp:
            row = df_cohort[
                (df_cohort["contract"] == c_name)
                & (df_cohort["tenure_band"] == b_name)
            ]
            if len(row) > 0:
                act_r = row["churn_rate_pct"].values[0]
                report(
                    f"Cohort churn %: {c_name} x {b_name} ({exp_r}%)",
                    abs(act_r - exp_r) <= RATE_TOL,
                    f"{act_r:.1f}%",
                )
            else:
                report(f"Cohort churn %: {c_name} x {b_name}", False, "Row not found")

    # small_group checks: exactly One year 0-6 (39), Two year 0-6 (29), Two year 7-12 (39)
    sg_rows = df_cohort[df_cohort["small_group"] == "Yes"]
    sg_set = set(zip(sg_rows["contract"], sg_rows["tenure_band"], sg_rows["customers"]))
    exp_sg_set = {
        ("One year", "0-6", 39),
        ("Two year", "0-6", 29),
        ("Two year", "7-12", 39),
    }

    report(
        "Cohort small_group=Yes exactly for One year 0-6 (39), Two year 0-6 (29), Two year 7-12 (39)",
        sg_set == exp_sg_set,
        str(sg_set),
    )
except Exception as e:
    report("Cohort table checks", False, f"Error: {e}")

# ===========================================================================
# 7. Churn Drivers Checks
# ===========================================================================
print("\n--- 7. churn_drivers.csv Checks ---")

df_drivers = None
drivers_path = TABLEAU_DIR / "churn_drivers.csv"

try:
    df_drivers = pd.read_csv(drivers_path)

    expected_drivers = [
        ("Payment Method", "Electronic check", 45.3),
        ("Internet Service", "Fiber optic", 41.9),
        ("Senior Citizen", "Yes", 41.7),
        ("Tech Support", "No", 41.6),
        ("Payment Method", "Mailed check", 19.1),
        ("Internet Service", "DSL", 19.0),
        ("Payment Method", "Bank transfer (automatic)", 16.7),
        ("Payment Method", "Credit card (automatic)", 15.2),
        ("Tech Support", "Yes", 15.2),
        ("Paperless Billing", "Yes", 33.6),
        ("Paperless Billing", "No", 16.3),
        ("Partner", "No", 33.0),
        ("Partner", "Yes", 19.7),
        ("Dependents", "No", 31.3),
        ("Dependents", "Yes", 15.5),
        ("Online Security", "No", 41.8),
        ("Online Security", "Yes", 14.6),
    ]

    for factor_val, cat_val, exp_r in expected_drivers:
        match = df_drivers[
            (df_drivers["factor"] == factor_val)
            & (df_drivers["category"] == cat_val)
        ]
        if len(match) > 0:
            act_r = match["churn_rate_pct"].values[0]
            report(
                f"Churn driver {factor_val}={cat_val} ({exp_r}%)",
                abs(act_r - exp_r) <= RATE_TOL,
                f"{act_r:.1f}%",
            )
        else:
            report(f"Churn driver {factor_val}={cat_val}", False, "Row not found")

except Exception as e:
    report("Churn drivers checks", False, f"Error: {e}")

# ===========================================================================
# Summary & Exit Code
# ===========================================================================
print("\n" + "=" * 70)
total_tests = passed_count + failed_count
print(f"  TOTAL CHECKS: {total_tests} | PASSED: {passed_count} | FAILED: {failed_count}")
print("=" * 70)

if failed_count > 0:
    print(f"\n❌ Verification failed with {failed_count} failing check(s).")
    sys.exit(1)
else:
    print("\n✅ All Tableau data verification checks passed successfully!")
    sys.exit(0)
