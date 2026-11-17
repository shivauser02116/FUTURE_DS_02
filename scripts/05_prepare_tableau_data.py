"""
scripts/05_prepare_tableau_data.py
==================================
Prepares Tableau-ready data files from data/telco_clean.csv and writes them into data/tableau/:
  1. telco_customers_tableau.csv (7,043 rows, 30 columns)
  2. retention_curve.csv (Kaplan-Meier survival curves by segment, 0-72 months)
  3. cohort_contract_tenure.csv (Contract x Tenure band matrix)
  4. churn_drivers.csv (Factor analysis with churn rates)

Usage:
    python3 scripts/05_prepare_tableau_data.py
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = REPO_ROOT / "data" / "telco_clean.csv"
OUTPUT_DIR = REPO_ROOT / "data" / "tableau"


def get_tenure_band(t: int) -> tuple[str, int]:
    """Map tenure in months to band and sort order (tenure 0 belongs in 0-6)."""
    if t <= 6:
        return "0-6", 1
    elif t <= 12:
        return "7-12", 2
    elif t <= 24:
        return "13-24", 3
    elif t <= 48:
        return "25-48", 4
    else:
        return "49-72", 5


def main():
    if not INPUT_PATH.is_file():
        print(f"ERROR: Missing input file {INPUT_PATH}")
        print("Please run scripts/01_clean_telco.py first.")
        sys.exit(1)

    print(f"Reading cleaned data from: {INPUT_PATH}")
    df = pd.read_csv(INPUT_PATH)
    n_rows = len(df)
    print(f"Loaded {n_rows} rows.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # =======================================================================
    # 1. telco_customers_tableau.csv
    # =======================================================================
    print("\n[1/4] Generating telco_customers_tableau.csv...")

    # Helper transformations
    bands, band_orders = zip(*df["tenure"].map(get_tenure_band))
    contract_order_map = {"Month-to-month": 1, "One year": 2, "Two year": 3}

    addon_cols = [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies",
    ]
    num_addons = df[addon_cols].apply(
        lambda row: int(sum(val == "Yes" for val in row)), axis=1
    )

    auto_pay = df["payment_method"].apply(
        lambda x: "Yes" if "(automatic)" in str(x) else "No"
    )

    tot_charges = pd.to_numeric(df["total_charges"], errors="coerce").fillna(0.0).round(2)
    m_charges = df["monthly_charges"].round(2)

    churned_rev = np.where(df["churn_flag"] == 1, m_charges, 0.0)
    churned_rev = np.round(churned_rev, 2)

    is_high_risk = (
        (df["contract"] == "Month-to-month")
        & (df["internet_service"] == "Fiber optic")
        & (df["payment_method"] == "Electronic check")
    )
    high_risk_segment = is_high_risk.map({True: "Yes", False: "No"})

    senior_citizen_val = df["senior_citizen"].fillna(
        df["seniorcitizen"].map({1: "Yes", 0: "No"})
    )

    df_customers = pd.DataFrame(
        {
            "customer_id": df["customer_id"],
            "customer_count": 1,
            "gender": df["gender"],
            "senior_citizen": senior_citizen_val,
            "partner": df["partner"],
            "dependents": df["dependents"],
            "tenure_months": df["tenure"].astype(int),
            "tenure_band": bands,
            "tenure_band_order": band_orders,
            "phone_service": df["phone_service"],
            "multiple_lines": df["multiple_lines"],
            "internet_service": df["internet_service"],
            "online_security": df["online_security"],
            "online_backup": df["online_backup"],
            "device_protection": df["device_protection"],
            "tech_support": df["tech_support"],
            "streaming_tv": df["streaming_tv"],
            "streaming_movies": df["streaming_movies"],
            "num_addon_services": num_addons,
            "contract": df["contract"],
            "contract_order": df["contract"].map(contract_order_map),
            "paperless_billing": df["paperless_billing"],
            "payment_method": df["payment_method"],
            "auto_pay": auto_pay,
            "monthly_charges": m_charges,
            "total_charges": tot_charges,
            "churn": df["churn"],
            "churn_flag": df["churn_flag"].astype(int),
            "churned_monthly_revenue": churned_rev,
            "high_risk_segment": high_risk_segment,
        }
    )

    cust_out = OUTPUT_DIR / "telco_customers_tableau.csv"
    df_customers.to_csv(cust_out, index=False, encoding="utf-8")
    print(f"✓ Wrote {len(df_customers)} rows to {cust_out}")

    # =======================================================================
    # 2. retention_curve.csv
    # =======================================================================
    print("\n[2/4] Generating retention_curve.csv...")

    # Exclude tenure == 0 customers
    km_data = df[df["tenure"] > 0].copy()

    segments = [
        ("Overall", "Overall", km_data),
        ("Contract", "Month-to-month", km_data[km_data["contract"] == "Month-to-month"]),
        ("Contract", "One year", km_data[km_data["contract"] == "One year"]),
        ("Contract", "Two year", km_data[km_data["contract"] == "Two year"]),
        ("Internet Service", "DSL", km_data[km_data["internet_service"] == "DSL"]),
        ("Internet Service", "Fiber optic", km_data[km_data["internet_service"] == "Fiber optic"]),
        ("Internet Service", "No", km_data[km_data["internet_service"] == "No"]),
    ]

    curve_rows = []
    for stype, sname, sub in segments:
        n_seg = len(sub)
        # Month 0
        curve_rows.append(
            {
                "segment_type": stype,
                "segment": sname,
                "month": 0,
                "at_risk": n_seg,
                "events": 0,
                "retention_pct": 100.00,
                "reliable": "Yes" if n_seg >= 100 else "No",
            }
        )

        S = 1.0
        for t in range(1, 73):
            at_risk = int((sub["tenure"] >= t).sum())
            events = int(((sub["tenure"] == t) & (sub["churn_flag"] == 1)).sum())
            if at_risk > 0:
                S = S * (1.0 - events / at_risk)
            else:
                S = 0.0
            reliable = "Yes" if at_risk >= 100 else "No"
            curve_rows.append(
                {
                    "segment_type": stype,
                    "segment": sname,
                    "month": t,
                    "at_risk": at_risk,
                    "events": events,
                    "retention_pct": round(S * 100.0, 2),
                    "reliable": reliable,
                }
            )

    df_retention = pd.DataFrame(curve_rows)
    ret_out = OUTPUT_DIR / "retention_curve.csv"
    df_retention.to_csv(ret_out, index=False, encoding="utf-8")
    print(f"✓ Wrote {len(df_retention)} rows to {ret_out}")

    # =======================================================================
    # 3. cohort_contract_tenure.csv
    # =======================================================================
    print("\n[3/4] Generating cohort_contract_tenure.csv...")

    cohort_rows = []
    tenure_bands_ordered = [("0-6", 1), ("7-12", 2), ("13-24", 3), ("25-48", 4), ("49-72", 5)]

    for c_name in ["Month-to-month", "One year", "Two year"]:
        c_ord = contract_order_map[c_name]
        for t_band, t_ord in tenure_bands_ordered:
            sub = df_customers[
                (df_customers["contract"] == c_name)
                & (df_customers["tenure_band"] == t_band)
            ]
            cust_count = len(sub)
            churned_count = int(sub["churn_flag"].sum())
            rate = round((churned_count / cust_count * 100) if cust_count > 0 else 0.0, 1)
            small = "Yes" if cust_count < 50 else "No"

            cohort_rows.append(
                {
                    "contract": c_name,
                    "contract_order": c_ord,
                    "tenure_band": t_band,
                    "tenure_band_order": t_ord,
                    "customers": cust_count,
                    "churned": churned_count,
                    "churn_rate_pct": rate,
                    "small_group": small,
                }
            )

    df_cohort = pd.DataFrame(cohort_rows)
    cohort_out = OUTPUT_DIR / "cohort_contract_tenure.csv"
    df_cohort.to_csv(cohort_out, index=False, encoding="utf-8")
    print(f"✓ Wrote {len(df_cohort)} rows to {cohort_out}")

    # =======================================================================
    # 4. churn_drivers.csv
    # =======================================================================
    print("\n[4/4] Generating churn_drivers.csv...")

    # Factors in order requested
    factors_spec = [
        ("Contract", df_customers["contract"], ["Month-to-month", "One year", "Two year"]),
        ("Internet Service", df_customers["internet_service"], ["DSL", "Fiber optic", "No"]),
        (
            "Payment Method",
            df_customers["payment_method"],
            [
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)",
            ],
        ),
        ("Tech Support", df_customers["tech_support"], ["No", "Yes", "No internet service"]),
        ("Online Security", df_customers["online_security"], ["No", "Yes", "No internet service"]),
        ("Senior Citizen", df_customers["senior_citizen"], ["Yes", "No"]),
        ("Paperless Billing", df_customers["paperless_billing"], ["Yes", "No"]),
        ("Partner", df_customers["partner"], ["No", "Yes"]),
        ("Dependents", df_customers["dependents"], ["No", "Yes"]),
        ("Tenure Band", df_customers["tenure_band"], ["0-6", "7-12", "13-24", "25-48", "49-72"]),
    ]

    driver_rows = []
    for factor_name, series, cat_order in factors_spec:
        for cat in cat_order:
            sub = df_customers[series == cat]
            c_cnt = len(sub)
            ch_cnt = int(sub["churn_flag"].sum())
            c_rate = round((ch_cnt / c_cnt * 100) if c_cnt > 0 else 0.0, 1)
            driver_rows.append(
                {
                    "factor": factor_name,
                    "category": cat,
                    "customers": c_cnt,
                    "churned": ch_cnt,
                    "churn_rate_pct": c_rate,
                }
            )

    df_drivers = pd.DataFrame(driver_rows)
    drivers_out = OUTPUT_DIR / "churn_drivers.csv"
    df_drivers.to_csv(drivers_out, index=False, encoding="utf-8")
    print(f"✓ Wrote {len(df_drivers)} rows to {drivers_out}")

    print("\nAll 4 Tableau files successfully written to data/tableau/!")


if __name__ == "__main__":
    main()
