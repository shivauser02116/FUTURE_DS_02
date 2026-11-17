# Tableau Data Dictionary — FUTURE_DS_02

This data dictionary documents the four Tableau-ready datasets generated in `data/tableau/` for the Telco Customer Churn analysis.

---

## 1. `telco_customers_tableau.csv` (Customer Level)

| Column | Description |
| :--- | :--- |
| `customer_id` | Unique alphanumeric identifier for each customer. |
| `customer_count` | Constant integer value (1) enabling simple `SUM(customer_count)` aggregation in Tableau. |
| `gender` | Customer gender classification (`Female`, `Male`). |
| `senior_citizen` | Senior citizen indicator status (`Yes`, `No`). |
| `partner` | Whether the customer has a partner (`Yes`, `No`). |
| `dependents` | Whether the customer has dependents (`Yes`, `No`). |
| `tenure_months` | Number of months the customer has stayed with the company (`0` to `72`). |
| `tenure_band` | Binned customer tenure category (`0-6`, `7-12`, `13-24`, `25-48`, `49-72`), with tenure 0 grouped into `0-6`. |
| `tenure_band_order` | Integer index (`1` to `5`) for chronological sorting of tenure bands in Tableau visuals. |
| `phone_service` | Whether the customer has landline phone service (`Yes`, `No`). |
| `multiple_lines` | Multi-line telephone service status (`No phone service`, `No`, `Yes`). |
| `internet_service` | Subscribed internet service provider technology (`DSL`, `Fiber optic`, `No`). |
| `online_security` | Add-on online security protection status (`No internet service`, `No`, `Yes`). |
| `online_backup` | Add-on cloud data backup service status (`No internet service`, `No`, `Yes`). |
| `device_protection` | Add-on device hardware warranty/protection status (`No internet service`, `No`, `Yes`). |
| `tech_support` | Add-on premium technical support service status (`No internet service`, `No`, `Yes`). |
| `streaming_tv` | Add-on live streaming television service status (`No internet service`, `No`, `Yes`). |
| `streaming_movies` | Add-on streaming video and movies service status (`No internet service`, `No`, `Yes`). |
| `num_addon_services` | Count of active optional add-on services from 0 to 6 (`online_security`, `online_backup`, `device_protection`, `tech_support`, `streaming_tv`, `streaming_movies`). |
| `contract` | Customer billing agreement commitment term (`Month-to-month`, `One year`, `Two year`). |
| `contract_order` | Integer sorting index for contracts (`Month-to-month` = 1, `One year` = 2, `Two year` = 3). |
| `paperless_billing` | Whether customer receives digital paperless bills (`Yes`, `No`). |
| `payment_method` | Customer billing transaction method (`Electronic check`, `Mailed check`, `Bank transfer (automatic)`, `Credit card (automatic)`). |
| `auto_pay` | Whether payment method is automated (`Yes` for Bank transfer and Credit card, else `No`). |
| `monthly_charges` | Current monthly recurring service fee in USD, rounded to 2 decimal places. |
| `total_charges` | Cumulative total charges billed across customer lifetime in USD, with initial blanks set to 0.00. |
| `churn` | Churn outcome label for the customer (`Yes`, `No`). |
| `churn_flag` | Numeric binary churn indicator (`1` for churned, `0` for retained). |
| `churned_monthly_revenue` | Monthly recurring revenue lost to churn (`monthly_charges` if `churn_flag` = 1, else `0.00`). |
| `high_risk_segment` | Indicator for highest-risk segment (`Yes` if Month-to-month AND Fiber optic AND Electronic check, else `No`). |

---

## 2. `retention_curve.csv` (Kaplan-Meier Survival Analysis)

| Column | Description |
| :--- | :--- |
| `segment_type` | High-level grouping dimension for survival analysis (`Overall`, `Contract`, `Internet Service`). |
| `segment` | Specific cohort segment analyzed (`Overall`, contract terms, or internet service tiers). |
| `month` | Customer lifetime timeline milestone from `0` to `72` months. |
| `at_risk` | Number of active customers remaining under observation at the beginning of month $t$. |
| `events` | Number of customers who churned exactly at month $t$. |
| `retention_pct` | Estimated Kaplan-Meier cumulative retention percentage $S(t) \times 100$ (0.00% to 100.00%). |
| `reliable` | Statistical reliability flag (`Yes` when sample size `at_risk` $\ge$ 100, else `No`). |

---

## 3. `cohort_contract_tenure.csv` (Contract x Tenure Matrix)

| Column | Description |
| :--- | :--- |
| `contract` | Customer contract term (`Month-to-month`, `One year`, `Two year`). |
| `contract_order` | Integer sorting index (`1` to `3`) for contract duration ordering. |
| `tenure_band` | Grouped customer lifecycle tenure band (`0-6`, `7-12`, `13-24`, `25-48`, `49-72`). |
| `tenure_band_order` | Integer sequence (`1` to `5`) for chronological ordering of tenure bands. |
| `customers` | Total number of customer accounts in the specific contract and tenure band cohort. |
| `churned` | Total number of churned customers in the cohort. |
| `churn_rate_pct` | Percentage of customers churned in the cohort, formatted to 1 decimal place. |
| `small_group` | Sample size warning indicator (`Yes` if `customers` < 50 for low statistical significance, else `No`). |

---

## 4. `churn_drivers.csv` (Factor Analysis)

| Column | Description |
| :--- | :--- |
| `factor` | Customer attribute or service feature analyzed (e.g., `Contract`, `Internet Service`, `Payment Method`). |
| `category` | Distinct category value within the factor (e.g., `Fiber optic`, `Electronic check`, `Senior Citizen = Yes`). |
| `customers` | Total number of customer accounts belonging to this category. |
| `churned` | Total number of customers who churned within this category. |
| `churn_rate_pct` | Observed churn rate percentage for the category, formatted to 1 decimal place. |

---

## How to Use in Tableau

1. **Sort `tenure_band` by `tenure_band_order`:** In Tableau, right-click the `tenure_band` field in the Data pane, choose **Default Properties > Sort**, select **By field**, and choose `tenure_band_order` (Aggregation: Minimum, Ascending).
2. **Sort `contract` by `contract_order`:** Right-click the `contract` dimension, choose **Default Properties > Sort**, select **By field**, and choose `contract_order` (Aggregation: Minimum, Ascending).
3. **Use `AVG(churn_flag)` for churn rate:** Drag `churn_flag` to Rows or Columns, change its aggregation to `Average` (`AVG`), and set number format to **Percentage** with 1 decimal place.
4. **Use `SUM(customer_count)` for customers:** Drag `customer_count` to your visual as a measure using `SUM` aggregation to count total customer accounts.
5. **Filter `reliable = Yes` on the retention curve:** When plotting `retention_curve.csv`, drag the `reliable` field to the Filters shelf and select `Yes` to suppress noisy estimates where sample sizes drop below 100 customers.
