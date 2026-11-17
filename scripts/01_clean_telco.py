"""
scripts/01_clean_telco.py
=========================
Cleans the raw Telco Customer Churn dataset and writes data/telco_clean.csv.

Raw source (Kaggle):
  WA_Fn-UseC_-Telco-Customer-Churn.csv  (or .xls)
  https://www.kaggle.com/datasets/blastchar/telco-customer-churn

Usage
-----
    python scripts/01_clean_telco.py [--raw <path_to_raw_file>]

If --raw is not supplied the script tries, in order:
  1. data/WA_Fn-UseC_-Telco-Customer-Churn.csv
  2. data/WA_Fn-UseC_-Telco-Customer-Churn.xls
  3. ~/Downloads/WA_Fn-UseC_-Telco-Customer-Churn.csv
  4. ~/Downloads/WA_Fn-UseC_-Telco-Customer-Churn.xls
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
OUT_PATH = DATA_DIR / "telco_clean.csv"
DOCS_DIR = PROJECT_ROOT / "docs"

RAW_CANDIDATES = [
    DATA_DIR / "WA_Fn-UseC_-Telco-Customer-Churn.csv",
    DATA_DIR / "WA_Fn-UseC_-Telco-Customer-Churn.xls",
    Path.home() / "Downloads" / "WA_Fn-UseC_-Telco-Customer-Churn.csv",
    Path.home() / "Downloads" / "WA_Fn-UseC_-Telco-Customer-Churn.xls",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_raw(raw_path: Path) -> pd.DataFrame:
    """Load raw file; supports .csv and .xls/.xlsx, with fallback."""
    try:
        return pd.read_csv(raw_path)
    except Exception:
        return pd.read_excel(raw_path)


def find_raw(cli_path: str | None) -> Path:
    """Return the first readable raw file, or raise."""
    if cli_path:
        p = Path(cli_path)
        if p.is_file():
            return p
        raise FileNotFoundError(f"--raw path not found: {p}")
    for candidate in RAW_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "Cannot find the raw Telco dataset. Supply it with --raw <path> or place it in data/."
    )


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------

def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    log: list[str] = []
    n_raw = len(df)
    log.append(f"Loaded {n_raw} rows × {df.shape[1]} columns.")

    # 1. Standardise column names
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )
    log.append("Standardised column names (lower_snake_case).")

    # 2. Trim string whitespace everywhere
    obj_cols = df.select_dtypes("object").columns
    df[obj_cols] = df[obj_cols].apply(lambda s: s.str.strip())

    # 3. totalcharges is stored as string in some exports — convert
    if "totalcharges" in df.columns:
        before = df["totalcharges"].isna().sum()
        df["totalcharges"] = pd.to_numeric(df["totalcharges"], errors="coerce")
        blanks = df["totalcharges"].isna().sum() - before
        if blanks:
            log.append(
                f"totalcharges: coerced {blanks} blank/non-numeric to NaN "
                f"(new customers with tenure=0)."
            )

    # 4. Fill totalcharges NaN with 0 (tenure=0 customers have no charges yet)
    if "totalcharges" in df.columns and df["totalcharges"].isna().any():
        df["totalcharges"] = df["totalcharges"].fillna(0.0)
        log.append("Filled totalcharges NaN → 0.0 (tenure=0 customers).")

    # 5. churn flag: Yes/No → 1/0
    if "churn" in df.columns:
        df["churn_flag"] = (df["churn"].str.lower() == "yes").astype(int)
        log.append("Created churn_flag (1=churned, 0=retained).")

    # 6. SeniorCitizen: already 0/1 in the raw; convert to str label for filtering
    if "seniorcitizen" in df.columns:
        df["senior_citizen"] = df["seniorcitizen"].map({0: "No", 1: "Yes"})
        log.append("Mapped seniorcitizen → senior_citizen ('Yes'/'No').")

    # 7. Rename key columns for readability
    rename_map = {
        "contract": "contract",
        "internetservice": "internet_service",
        "paymentmethod": "payment_method",
        "monthlycharges": "monthly_charges",
        "totalcharges": "total_charges",
        "tenure": "tenure",
        "customerid": "customer_id",
        "paperlessbilling": "paperless_billing",
        "techsupport": "tech_support",
        "onlinesecurity": "online_security",
        "onlinebackup": "online_backup",
        "deviceprotection": "device_protection",
        "streamingtv": "streaming_tv",
        "streamingmovies": "streaming_movies",
        "phoneservice": "phone_service",
        "multiplelines": "multiple_lines",
        "dependents": "dependents",
        "partner": "partner",
        "gender": "gender",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    log.append("Renamed columns to consistent snake_case.")

    # 8. Remove exact duplicates
    n_before = len(df)
    df = df.drop_duplicates()
    n_dupes = n_before - len(df)
    if n_dupes:
        log.append(f"Removed {n_dupes} exact duplicate row(s).")
    else:
        log.append("No exact duplicates found.")

    # 9. Tenure band
    bins = [0, 6, 12, 24, 48, 72]
    labels = ["0–6 mo", "7–12 mo", "13–24 mo", "25–48 mo", "49–72 mo"]
    df["tenure_band"] = pd.cut(
        df["tenure"],
        bins=bins,
        labels=labels,
        right=True,
        include_lowest=True,
    )
    log.append("Added tenure_band column (5 bands: 0-6, 7-12, 13-24, 25-48, 49-72).")

    # 10. Final shape
    log.append(f"Output: {len(df)} rows × {df.shape[1]} columns.")
    return df, log


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Clean Telco Customer Churn dataset.")
    parser.add_argument("--raw", default=None, help="Path to the raw CSV or XLS file.")
    args = parser.parse_args()

    try:
        raw_path = find_raw(args.raw)
    except FileNotFoundError as exc:
        print(f"\n❌  {exc}")
        print(
            "\nDownload the dataset from:\n"
            "  https://www.kaggle.com/datasets/blastchar/telco-customer-churn\n"
            "and place the file in data/ or ~/Downloads/ then re-run this script."
        )
        sys.exit(1)

    print(f"Loading raw data from: {raw_path}")
    df_raw = load_raw(raw_path)

    df_clean, log = clean(df_raw)

    # Write output
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(OUT_PATH, index=False)
    print(f"\n✓  Wrote {len(df_clean)} rows to: {OUT_PATH}\n")

    # Write cleaning log
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = DOCS_DIR / "cleaning_log.md"
    with open(log_path, "w") as fh:
        fh.write("# Data Cleaning Log\n\n")
        fh.write(f"**Source file:** `{raw_path.name}`  \n")
        fh.write(f"**Output file:** `data/telco_clean.csv`  \n\n")
        fh.write("## Steps\n\n")
        for i, entry in enumerate(log, 1):
            fh.write(f"{i}. {entry}\n")
    print(f"✓  Cleaning log written to: {log_path}")

    # Print a summary
    print("\n--- Cleaning summary ---")
    for entry in log:
        print(f"  • {entry}")


if __name__ == "__main__":
    main()
