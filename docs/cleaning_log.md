# Data Cleaning Log

**Source file:** `WA_Fn-UseC_-Telco-Customer-Churn.xls`  
**Output file:** `data/telco_clean.csv`  

## Steps

1. Loaded 7043 rows × 21 columns.
2. Standardised column names (lower_snake_case).
3. totalcharges: coerced 11 blank/non-numeric to NaN (new customers with tenure=0).
4. Filled totalcharges NaN → 0.0 (tenure=0 customers).
5. Created churn_flag (1=churned, 0=retained).
6. Mapped seniorcitizen → senior_citizen ('Yes'/'No').
7. Renamed columns to consistent snake_case.
8. No exact duplicates found.
9. Added tenure_band column (5 bands: 0-6, 7-12, 13-24, 25-48, 49-72).
10. Output: 7043 rows × 24 columns.
