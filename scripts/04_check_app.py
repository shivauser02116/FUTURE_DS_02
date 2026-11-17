"""
scripts/04_check_app.py
=======================
Automated verification suite for the FUTURE_DS_02 Streamlit application
and underlying customer retention dataset.

Run from repository root:
    python3 scripts/04_check_app.py

Requirements: streamlit >= 1.50, pandas, numpy, plotly
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

# ---------------------------------------------------------------------------
# Paths & Settings
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
APP_PATH = REPO_ROOT / "app" / "streamlit_app.py"
CSV_PATH = REPO_ROOT / "data" / "telco_clean.csv"

TOL = 0.005  # 0.5% numerical tolerance
passed_count = 0
failed_count = 0


def check(label: str, passed: bool, actual: str) -> None:
    """Record test result and print formatted output."""
    global passed_count, failed_count
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {label}: {actual}")
    if passed:
        passed_count += 1
    else:
        failed_count += 1


def within(actual: float, expected: float, tol: float = TOL) -> bool:
    """Check if actual is within relative tolerance of expected."""
    if expected == 0:
        return abs(actual) < 1e-9
    return abs(actual - expected) / abs(expected) <= tol


print("=" * 70)
print("  FUTURE_DS_02: Streamlit App & Data Verification Suite")
print("=" * 70)

# ===========================================================================
# SECTION A: AppTest Framework Checks (UI, KPIs, Filters, Navigation)
# ===========================================================================
print("\n--- SECTION A: Streamlit UI & Interactivity (AppTest) ---\n")

# A1: Default run without exceptions
at = AppTest.from_file(str(APP_PATH), default_timeout=45)
try:
    at.run()
    no_exc = len(at.exception) == 0
    check(
        "A1: Default run produces no exceptions",
        no_exc,
        "Clean run (0 exceptions)" if no_exc else f"Errors: {[e.value for e in at.exception]}",
    )
except Exception as e:
    check("A1: Default run produces no exceptions", False, f"Exception: {e}")

# A2-A7: Baseline KPI metric checks
try:
    metrics = {m.label: m.value for m in at.metric}
    check(
        "A2: KPI Customers metric",
        metrics.get("Customers") == "7,043",
        metrics.get("Customers", "<not found>"),
    )
except Exception as e:
    check("A2: KPI Customers metric", False, f"Error: {e}")

try:
    metrics = {m.label: m.value for m in at.metric}
    check(
        "A3: KPI Churn rate metric",
        metrics.get("Churn rate") == "26.5%",
        metrics.get("Churn rate", "<not found>"),
    )
except Exception as e:
    check("A3: KPI Churn rate metric", False, f"Error: {e}")

try:
    metrics = {m.label: m.value for m in at.metric}
    check(
        "A4: KPI Churned customers metric",
        metrics.get("Churned customers") == "1,869",
        metrics.get("Churned customers", "<not found>"),
    )
except Exception as e:
    check("A4: KPI Churned customers metric", False, f"Error: {e}")

try:
    metrics = {m.label: m.value for m in at.metric}
    check(
        "A5: KPI Monthly revenue lost to churn",
        metrics.get("Monthly revenue lost to churn") == "$139K",
        metrics.get("Monthly revenue lost to churn", "<not found>"),
    )
except Exception as e:
    check("A5: KPI Monthly revenue lost to churn", False, f"Error: {e}")

try:
    metrics = {m.label: m.value for m in at.metric}
    check(
        "A6: KPI Avg monthly charge",
        metrics.get("Avg monthly charge") == "$74.44",
        metrics.get("Avg monthly charge", "<not found>"),
    )
except Exception as e:
    check("A6: KPI Avg monthly charge", False, f"Error: {e}")

try:
    metrics = {m.label: m.value for m in at.metric}
    check(
        "A7: KPI Avg tenure",
        metrics.get("Avg tenure") == "18.0",
        metrics.get("Avg tenure", "<not found>"),
    )
except Exception as e:
    check("A7: KPI Avg tenure", False, f"Error: {e}")

# A8: Tabs order and naming
try:
    expected_tabs = ["Overview", "Churn drivers", "Customer lifetime", "Action plan"]
    actual_tabs = [t.label for t in at.tabs]
    check(
        "A8: Four tabs match Figma frames in exact order",
        actual_tabs == expected_tabs,
        str(actual_tabs),
    )
except Exception as e:
    check("A8: Four tabs match Figma frames in exact order", False, f"Error: {e}")

# A9: Sidebar multiselect filters exist
try:
    ms_labels = [w.label for w in at.multiselect]
    expected_filters = ["Contract", "Internet Service", "Senior Citizen"]
    filters_present = all(f in ms_labels for f in expected_filters)
    check(
        "A9: Sidebar multiselect filters exist",
        filters_present,
        f"Found {ms_labels}",
    )
except Exception as e:
    check("A9: Sidebar multiselect filters exist", False, f"Error: {e}")

# A10: Filter responsiveness (Deselecting Month-to-month)
try:
    contract_widget = next(w for w in at.multiselect if w.label == "Contract")
    contract_widget.set_value(["One year", "Two year"])
    at.run()

    no_exc_filter = len(at.exception) == 0
    new_metrics = {m.label: m.value for m in at.metric}
    new_cust = new_metrics.get("Customers", "")
    new_churn = new_metrics.get("Churn rate", "")
    responsive = (new_cust == "3,168") and (new_churn == "6.8%")

    check(
        "A10: Filter responsiveness (Contract = One year, Two year)",
        no_exc_filter and responsive,
        f"Customers={new_cust}, Churn rate={new_churn}",
    )
except Exception as e:
    check("A10: Filter responsiveness (Contract = One year, Two year)", False, f"Error: {e}")

# A11: Empty filter handling (Guard against crash)
try:
    contract_widget = next(w for w in at.multiselect if w.label == "Contract")
    contract_widget.set_value([])
    at.run()

    no_crash = len(at.exception) == 0
    has_warning = len(at.warning) > 0
    warn_text = at.warning[0].value if has_warning else ""
    check(
        "A11: Empty filter guard triggers friendly warning without crashing",
        no_crash and has_warning,
        f"Warnings={len(at.warning)}, Message='{warn_text[:60]}...'",
    )
except Exception as e:
    check("A11: Empty filter guard triggers friendly warning without crashing", False, f"Error: {e}")

# Reset AppTest for text and caption checks
try:
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()
    all_markdown_text = " ".join([m.value or "" for m in at.markdown])

    # A12: Churn drivers disclaimer
    req_driver_caption = "These are factors associated with churn, not proven causes."
    check(
        "A12: Churn drivers disclaimer caption present",
        req_driver_caption in all_markdown_text,
        "Found in markdown" if req_driver_caption in all_markdown_text else "Missing",
    )

    # A13: Customer lifetime caption
    req_km_caption = "Retention estimated from tenure (Kaplan-Meier)"
    check(
        "A13: Customer lifetime Kaplan-Meier caption present",
        req_km_caption in all_markdown_text,
        "Found in markdown" if req_km_caption in all_markdown_text else "Missing",
    )

    # A14: Action plan segment description
    req_segment_title = "Month-to-month + fiber optic + electronic check"
    check(
        "A14: Action plan highest-risk segment title present",
        req_segment_title in all_markdown_text,
        "Found in markdown" if req_segment_title in all_markdown_text else "Missing",
    )
except Exception as e:
    check("A12-A14 Markdown text checks", False, f"Error: {e}")

# ===========================================================================
# SECTION A (NEW): Enhanced App Checks (Footers, Sidebar, Cohort View, Expander)
# ===========================================================================
print("\n--- SECTION A (NEW): Footer, Sidebar, Cohort View & Expander Checks ---\n")

# A15: Footers contain FUTURE_DS_02 and NOT FUTURE_DS_01 or Mockup; sidebar has NO Figma
try:
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()
    all_md_text = " ".join([m.value or "" for m in at.markdown])
    sidebar_text = " ".join(
        [m.value or "" for m in at.sidebar.markdown] + [w.label for w in at.multiselect]
    )

    has_fut2 = "FUTURE_DS_02" in all_md_text
    no_fut1 = "FUTURE_DS_01" not in all_md_text
    no_mockup = "mockup" not in all_md_text.lower()
    no_figma = "figma" not in sidebar_text.lower()

    footer_ok = has_fut2 and no_fut1 and no_mockup and no_figma
    check(
        "A15: Footers have FUTURE_DS_02 (no FUTURE_DS_01/Mockup) & sidebar has no Figma",
        footer_ok,
        f"has_DS_02={has_fut2}, no_DS_01={no_fut1}, no_mockup={no_mockup}, no_figma_sidebar={no_figma}",
    )
except Exception as e:
    check("A15: Footer and sidebar branding checks", False, f"Error: {e}")

# A16: Required phrases: "not proven causes", "Cohort view", "About this analysis"
try:
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()
    all_md_text = " ".join([m.value or "" for m in at.markdown])
    has_npc = "not proven causes" in all_md_text
    has_cv = "Cohort view" in all_md_text
    has_expander = any("About this analysis" in (e.label or "") for e in at.expander) or (
        "About this analysis" in all_md_text
    )

    phrases_ok = has_npc and has_cv and has_expander
    check(
        "A16: Key sections present ('not proven causes', 'Cohort view', 'About this analysis')",
        phrases_ok,
        f"not_proven_causes={has_npc}, cohort_view={has_cv}, about_analysis={has_expander}",
    )
except Exception as e:
    check("A16: Required phrases presence", False, f"Error: {e}")

# A17: Deselect "Two year", then select only "Month-to-month" and "Fiber optic"
try:
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()

    contract_widget = next(w for w in at.multiselect if w.label == "Contract")
    contract_widget.set_value(["Month-to-month", "One year"])
    at.run()

    no_exc_step1 = len(at.exception) == 0
    text_step1 = " ".join([m.value or "" for m in at.markdown])
    cohort_rendered_step1 = "Cohort view" in text_step1

    # Step 2: select only Month-to-month and Fiber optic
    internet_widget = next(w for w in at.multiselect if w.label == "Internet Service")
    contract_widget.set_value(["Month-to-month"])
    internet_widget.set_value(["Fiber optic"])
    at.run()

    no_exc_step2 = len(at.exception) == 0

    filter_drilldown_ok = no_exc_step1 and cohort_rendered_step1 and no_exc_step2
    check(
        "A17: Contract filter drilldown (Deselect Two year, then Month-to-month + Fiber optic)",
        filter_drilldown_ok,
        f"step1_no_exc={no_exc_step1}, cohort_rendered={cohort_rendered_step1}, step2_no_exc={no_exc_step2}",
    )
except Exception as e:
    check("A17: Filter drilldown verification", False, f"Error: {e}")

# A18: Default filters KPI exact texts (7,043, 26.5%, 1,869, $139K, $74.44, 18.0, 37.6)
try:
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()

    no_exc_def = len(at.exception) == 0
    metric_text = " ".join([f"{m.label} {m.value} {m.delta or ''}" for m in at.metric])

    kpi_tokens = ["7,043", "26.5%", "1,869", "$139K", "$74.44", "18.0", "37.6"]
    tokens_found = {tok: tok in metric_text for tok in kpi_tokens}
    all_tokens_present = all(tokens_found.values()) and no_exc_def

    check(
        "A18: Default filters KPI texts (7,043, 26.5%, 1,869, $139K, $74.44, 18.0, 37.6)",
        all_tokens_present,
        f"All tokens present: {tokens_found}",
    )
except Exception as e:
    check("A18: Default filters KPI exact texts", False, f"Error: {e}")


# ===========================================================================
# SECTION B: Data & Kaplan-Meier Mathematical Correctness
# ===========================================================================
print("\n--- SECTION B: Data & Mathematical Validation ---\n")

# B1: Data file existence and row count
try:
    df_clean = pd.read_csv(CSV_PATH)
    check(
        "B1: Clean dataset exists with 7,043 rows",
        len(df_clean) == 7043,
        f"Loaded {len(df_clean)} rows",
    )
except Exception as e:
    check("B1: Clean dataset exists with 7,043 rows", False, f"Error: {e}")
    df_clean = None

# B2: Kaplan-Meier calculation validation
if df_clean is not None:
    try:
        km_sample = df_clean[df_clean["tenure"] > 0]
        km_expected = {
            "Month-to-month": {12: 70.3, 24: 58.6, 48: 39.7},
            "One year": {12: 99.1, 24: 97.8, 48: 91.7},
            "Two year": {12: 100.0, 24: 100.0, 48: 99.6},
        }

        all_km_passed = True
        km_details = []

        for contract_name, milestones in km_expected.items():
            sub = km_sample[km_sample["contract"] == contract_name]
            S = 1.0
            t_curve = {0: 100.0}
            for t in range(1, 73):
                at_risk = int((sub["tenure"] >= t).sum())
                if at_risk < 100:
                    break
                events = int(((sub["tenure"] == t) & (sub["churn_flag"] == 1)).sum())
                S = S * (1.0 - events / at_risk)
                t_curve[t] = S * 100.0

            for m, exp_val in milestones.items():
                act_val = t_curve.get(m, 0.0)
                is_close = within(act_val, exp_val, tol=0.01)
                if not is_close:
                    all_km_passed = False
                km_details.append(f"{contract_name}@{m}m: {act_val:.1f}% (exp {exp_val}%)")

        check(
            "B2: Kaplan-Meier retention values at 12, 24, 48 months match expected",
            all_km_passed,
            "; ".join(km_details[:3]) + " ...",
        )
    except Exception as e:
        check("B2: Kaplan-Meier retention values at 12, 24, 48 months match expected", False, f"Error: {e}")

# B3: Highest-risk segment stats verification
if df_clean is not None:
    try:
        seg = df_clean[
            (df_clean["contract"] == "Month-to-month")
            & (df_clean["internet_service"] == "Fiber optic")
            & (df_clean["payment_method"] == "Electronic check")
        ]
        seg_n = len(seg)
        seg_cr = seg["churn_flag"].mean() * 100
        seg_share = (seg["churn_flag"].sum() / df_clean["churn_flag"].sum()) * 100

        seg_ok = (seg_n == 1307) and within(seg_cr, 60.4, 0.01) and within(seg_share, 42.2, 0.01)
        check(
            "B3: Highest-risk segment metrics (1,307 customers, 60.4% churn, 42.2% share)",
            seg_ok,
            f"count={seg_n}, churn_rate={seg_cr:.1f}%, share={seg_share:.1f}%",
        )
    except Exception as e:
        check("B3: Highest-risk segment metrics (1,307 customers, 60.4% churn, 42.2% share)", False, f"Error: {e}")

# ===========================================================================
# SUMMARY
# ===========================================================================
total_tests = passed_count + failed_count

print("\n" + "=" * 70)
print(f"  TEST SUMMARY: {passed_count}/{total_tests} checks passed.")
print("=" * 70)

if failed_count > 0:
    print(f"\n❌ {failed_count} check(s) failed.")
    sys.exit(1)
else:
    print("\n✅ All checks passed successfully!")
    sys.exit(0)
