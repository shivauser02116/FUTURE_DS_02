"""
app/streamlit_app.py
====================
Interactive Streamlit application for Telco Customer Churn Analysis (FUTURE_DS_02).
Executive dashboard with four tabs:
  1. Overview
  2. Churn drivers
  3. Customer lifetime (including live cohort heatmap)
  4. Action plan (including expandable about section)
"""

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Page configuration & Styling
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Telco Churn Analytics | FUTURE_DS_02",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS matching executive dashboard design tokens
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

      :root {
        --navy: #1f3a5f;
        --navy-deep: #152b48;
        --teal: #2a9d8f;
        --red: #d1495b;
        --light: #f2f5fa;
        --ink: #172b45;
        --muted: #64748b;
        --border: #dfe6ef;
      }

      html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--ink);
      }

      /* Frame Header Banner */
      .frame-header {
        background-color: #1f3a5f;
        color: #ffffff;
        padding: 24px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .frame-header .eyebrow {
        color: #a9ded7;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 6px;
      }
      .frame-header h1 {
        color: #ffffff !important;
        font-size: 26px !important;
        font-weight: 600 !important;
        letter-spacing: -0.025em;
        margin: 0 !important;
      }
      .header-mark {
        display: flex;
        height: 38px;
        align-items: flex-end;
        gap: 6px;
        opacity: 0.9;
      }
      .header-mark span {
        width: 7px;
        border-radius: 5px 5px 0 0;
        background: #2a9d8f;
        display: inline-block;
      }
      .header-mark span:nth-child(1) { height: 16px; }
      .header-mark span:nth-child(2) { height: 27px; }
      .header-mark span:nth-child(3) { height: 38px; }

      /* KPI Cards */
      div[data-testid="stMetric"] {
        background-color: #f2f5fa;
        border: 1px solid #e7ebf2;
        border-radius: 15px;
        padding: 16px 20px;
        position: relative;
        overflow: hidden;
      }
      div[data-testid="stMetric"] label {
        color: #5e6e82 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
      }
      div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 27px !important;
        font-weight: 700 !important;
        color: #1f3a5f;
        line-height: 1.1;
      }
      div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
        color: #748296 !important;
        font-size: 11px !important;
        font-weight: 500 !important;
      }

      /* Hide misleading delta arrows completely */
      div[data-testid="stMetricDeltaIcon"] {
        display: none !important;
      }
      div[data-testid="stMetricDelta"] svg {
        display: none !important;
      }

      /* Distinct Card Left Borders */
      div[data-testid="column"]:nth-child(1) div[data-testid="stMetric"] {
        border-left: 4px solid #1f3a5f;
      }
      div[data-testid="column"]:nth-child(2) div[data-testid="stMetric"],
      div[data-testid="column"]:nth-child(3) div[data-testid="stMetric"] {
        border-left: 4px solid #d1495b;
      }

      /* Callout takeaway */
      .takeaway {
        padding: 14px 18px;
        color: #53657c;
        font-size: 12px;
        font-weight: 500;
        border-left: 4px solid #2a9d8f;
        border-radius: 0 9px 9px 0;
        background: #edf8f6;
        margin-top: 16px;
      }

      /* Risk Callout */
      .risk-callout {
        padding: 26px 30px;
        color: #ffffff;
        border-radius: 16px;
        background: #1f3a5f;
        box-shadow: 0 10px 30px rgba(31, 58, 95, 0.15);
        margin-bottom: 24px;
      }
      .risk-label {
        display: inline-block;
        padding: 6px 10px;
        color: #ffffff;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        border-radius: 6px;
        background: #d1495b;
      }
      .risk-callout h2 {
        color: #ffffff !important;
        margin-top: 14px;
        font-size: 22px !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
      }
      .risk-stats {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        margin-top: 20px;
        padding-top: 18px;
        border-top: 1px solid rgba(255, 255, 255, 0.18);
        gap: 20px;
      }
      .risk-stats strong {
        display: block;
        color: #ffffff;
        font-size: 26px;
        font-weight: 700;
      }
      .risk-stats span {
        display: block;
        margin-top: 4px;
        color: #bac8d8;
        font-size: 11px;
        font-weight: 500;
      }

      /* Recommendation Cards with equal height */
      .rec-card {
        background: #f2f5fa;
        border: 1px solid #dfe6ef;
        border-radius: 14px;
        padding: 22px;
        height: 140px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
      }
      .rec-badge {
        display: inline-flex;
        width: 30px;
        height: 30px;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-size: 12px;
        font-weight: 700;
        border-radius: 8px;
        background: #2a9d8f;
        margin-bottom: 12px;
        flex-shrink: 0;
      }
      .rec-card h4 {
        color: #1f3a5f !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        line-height: 1.4 !important;
        margin: 0 !important;
      }

      /* Section Kicker */
      .section-kicker {
        color: #2a9d8f;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 4px;
      }
      .section-heading-title {
        color: #1f3a5f;
        font-size: 18px;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 16px;
      }

      /* Cohort Heatmap Table */
      .cohort-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 8px;
        margin: 16px 0;
      }
      .cohort-table th {
        color: #5e6e82;
        font-size: 12px;
        font-weight: 600;
        text-align: center;
        padding: 8px 12px;
      }
      .cohort-table th:first-child {
        text-align: left;
      }
      .cohort-table td {
        padding: 14px 10px;
        text-align: center;
        border-radius: 10px;
        border: 1px solid #dfe6ef;
      }
      .cohort-table td.row-label {
        color: #1f3a5f;
        font-weight: 600;
        font-size: 13px;
        text-align: left;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
      }
      .cohort-table .cell-rate {
        font-size: 15px;
        font-weight: 700;
      }
      .cohort-table .cell-count {
        font-size: 11px;
        opacity: 0.85;
        margin-top: 3px;
      }

      /* Footer */
      .frame-footer {
        padding: 20px 0 10px 0;
        color: #78879a;
        font-size: 11px;
        letter-spacing: 0.01em;
        border-top: 1px solid #edf0f4;
        margin-top: 32px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Data loading (cached with pathlib relative to file)
# ---------------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    data_path = Path(__file__).resolve().parent.parent / "data" / "telco_clean.csv"
    if not data_path.is_file():
        st.error(
            f"Dataset not found at `{data_path}`. "
            "Please run `python scripts/01_clean_telco.py` first."
        )
        st.stop()
    df = pd.read_csv(data_path)
    return df


df_raw = load_data()

# ---------------------------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------------------------
st.sidebar.markdown(
    """
    <div style="padding-bottom: 12px;">
      <h3 style="color: #1f3a5f; margin:0; font-size: 18px;">Telco Churn Analytics</h3>
      <p style="color: #64748b; font-size: 12px; margin-top: 4px;">Customer retention & churn analysis</p>
    </div>
    """,
    unsafe_allow_html=True,
)

contract_opts = sorted(df_raw["contract"].dropna().unique().tolist())
selected_contract = st.sidebar.multiselect(
    "Contract",
    options=contract_opts,
    default=contract_opts,
)

internet_opts = sorted(df_raw["internet_service"].dropna().unique().tolist())
selected_internet = st.sidebar.multiselect(
    "Internet Service",
    options=internet_opts,
    default=internet_opts,
)

senior_opts = sorted(df_raw["senior_citizen"].dropna().unique().tolist())
selected_senior = st.sidebar.multiselect(
    "Senior Citizen",
    options=senior_opts,
    default=senior_opts,
)

# Filter the data
df = df_raw[
    (df_raw["contract"].isin(selected_contract))
    & (df_raw["internet_service"].isin(selected_internet))
    & (df_raw["senior_citizen"].isin(selected_senior))
].copy()

# Empty filter guard
if len(df) == 0:
    st.warning("No customers match the current filter selection. Please broaden your filters.")
    st.stop()

# Helper footer on every tab
def render_footer():
    st.markdown(
        '<div class="frame-footer">Source: Telco Customer Churn dataset (Kaggle). Analysis in FUTURE_DS_02.</div>',
        unsafe_allow_html=True,
    )

def render_banner(eyebrow: str, title: str):
    st.markdown(
        f"""
        <header class="frame-header">
          <div>
            <p class="eyebrow">{eyebrow}</p>
            <h1>{title}</h1>
          </div>
          <div class="header-mark" aria-hidden="true">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </header>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Tabs Navigation
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Churn drivers",
    "Customer lifetime",
    "Action plan",
])

# ===========================================================================
# TAB 1: OVERVIEW
# ===========================================================================
with tab1:
    render_banner("Overview", "Customer Retention & Churn Overview")

    n_cust = len(df)
    n_churn = int(df["churn_flag"].sum())
    churn_rate = (n_churn / n_cust * 100) if n_cust > 0 else 0.0

    total_monthly_rev = df["monthly_charges"].sum()
    churn_monthly_rev = df[df["churn_flag"] == 1]["monthly_charges"].sum()
    rev_lost_share = (churn_monthly_rev / total_monthly_rev * 100) if total_monthly_rev > 0 else 0.0

    churned_df = df[df["churn_flag"] == 1]
    retained_df = df[df["churn_flag"] == 0]

    avg_charge_churn = churned_df["monthly_charges"].mean() if len(churned_df) > 0 else 0.0
    avg_charge_ret = retained_df["monthly_charges"].mean() if len(retained_df) > 0 else 0.0

    avg_ten_churn = churned_df["tenure"].mean() if len(churned_df) > 0 else 0.0
    avg_ten_ret = retained_df["tenure"].mean() if len(retained_df) > 0 else 0.0

    # 6 KPI Metric Cards in 2 rows of 3 columns
    # delta_color="off" with CSS hiding arrow icons eliminates misleading arrows
    c1, c2, c3 = st.columns(3)
    c1.metric(
        label="Customers",
        value=f"{n_cust:,}",
    )
    c2.metric(
        label="Churn rate",
        value=f"{churn_rate:.1f}%",
    )
    c3.metric(
        label="Churned customers",
        value=f"{n_churn:,}",
    )

    st.write("")  # spacing

    c4, c5, c6 = st.columns(3)
    c4.metric(
        label="Monthly revenue lost to churn",
        value=f"${churn_monthly_rev / 1e3:.0f}K",
        delta=f"{rev_lost_share:.1f}% of ${total_monthly_rev / 1e3:.0f}K",
        delta_color="off",
    )
    c5.metric(
        label="Avg monthly charge",
        value=f"${avg_charge_churn:.2f}",
        delta=f"churned vs retained ${avg_charge_ret:.2f}",
        delta_color="off",
    )
    c6.metric(
        label="Avg tenure",
        value=f"{avg_ten_churn:.1f}",
        delta=f"churned vs retained {avg_ten_ret:.1f} months",
        delta_color="off",
    )

    st.write("")
    st.write("")

    # Two vertical bar charts
    col_chart1, col_chart2 = st.columns([0.45, 0.55])

    with col_chart1:
        st.markdown('<div class="section-heading-title">Churn rate by contract</div>', unsafe_allow_html=True)
        contract_order = ["Month-to-month", "One year", "Two year"]
        contract_data = (
            df.groupby("contract")["churn_flag"]
            .agg(rate=lambda x: x.mean() * 100)
            .reindex(contract_order)
            .dropna()
            .reset_index()
        )

        fig_contract = go.Figure()
        fig_contract.add_trace(
            go.Bar(
                x=contract_data["contract"],
                y=contract_data["rate"],
                text=[f"{v:.1f}%" for v in contract_data["rate"]],
                textposition="outside",
                textfont=dict(color="#D1495B", size=13, family="Inter", weight="bold"),
                marker=dict(
                    color="#D1495B",
                    cornerradius=6,
                ),
                width=0.45,
            )
        )
        max_c = max(contract_data["rate"]) if len(contract_data) > 0 else 50
        fig_contract.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=30, b=40),
            yaxis=dict(range=[0, max_c * 1.25], showgrid=True, gridcolor="#EDF0F4", visible=False),
            xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#5D6D81")),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_contract, width="stretch")

    with col_chart2:
        st.markdown('<div class="section-heading-title">Churn rate by tenure</div>', unsafe_allow_html=True)
        band_order = ["0–6 mo", "7–12 mo", "13–24 mo", "25–48 mo", "49–72 mo"]
        tb_data = (
            df.groupby("tenure_band", observed=False)["churn_flag"]
            .agg(rate=lambda x: x.mean() * 100)
            .reindex(band_order)
            .dropna()
            .reset_index()
        )
        display_labels = [
            b.replace(" mo", "") if b != "0–6 mo" else b for b in tb_data["tenure_band"]
        ]

        fig_tenure = go.Figure()
        fig_tenure.add_trace(
            go.Bar(
                x=display_labels,
                y=tb_data["rate"],
                text=[f"{v:.1f}%" for v in tb_data["rate"]],
                textposition="outside",
                textfont=dict(color="#D1495B", size=13, family="Inter", weight="bold"),
                marker=dict(
                    color="#D1495B",
                    cornerradius=6,
                ),
                width=0.48,
            )
        )
        max_t = max(tb_data["rate"]) if len(tb_data) > 0 else 60
        fig_tenure.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=30, b=40),
            yaxis=dict(range=[0, max_t * 1.25], showgrid=True, gridcolor="#EDF0F4", visible=False),
            xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#5D6D81")),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_tenure, width="stretch")

    render_footer()

# ===========================================================================
# TAB 2: CHURN DRIVERS
# ===========================================================================
with tab2:
    render_banner("Churn drivers", "Factors associated with customer churn")

    st.markdown('<p class="section-kicker">Ranked by churn rate</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 16px;">
          <h2 style="color: #1f3a5f; margin: 0; font-size: 20px; font-weight: 700;">Where churn is concentrated</h2>
          <span style="color: #7a8798; font-size: 12px; font-weight: 600;">Churn rate</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    factors_spec = [
        ("Electronic check", df["payment_method"] == "Electronic check"),
        ("Fiber optic", df["internet_service"] == "Fiber optic"),
        ("Senior citizens", df["senior_citizen"] == "Yes"),
        ("No tech support", df["tech_support"] == "No"),
        ("Mailed check", df["payment_method"] == "Mailed check"),
        ("DSL", df["internet_service"] == "DSL"),
        ("Bank transfer", df["payment_method"] == "Bank transfer (automatic)"),
        ("Credit card", df["payment_method"] == "Credit card (automatic)"),
        ("With tech support", df["tech_support"] == "Yes"),
    ]

    driver_rows = []
    for label, mask in factors_spec:
        subset = df[mask]
        if len(subset) > 0:
            rate = subset["churn_flag"].mean() * 100
            driver_rows.append({"label": label, "rate": rate, "count": len(subset)})

    driver_df = pd.DataFrame(driver_rows).sort_values("rate", ascending=False).reset_index(drop=True)

    if len(driver_df) > 0:
        plot_df = driver_df.iloc[::-1].reset_index(drop=True)
        colors = [
            "#D1495B" if idx >= len(plot_df) - 4 else "#DD7B88"
            for idx in range(len(plot_df))
        ]

        fig_drivers = go.Figure()
        fig_drivers.add_trace(
            go.Bar(
                y=plot_df["label"],
                x=plot_df["rate"],
                orientation="h",
                text=[f"  <b>{r:.1f}%</b>" for r in plot_df["rate"]],
                textposition="outside",
                textfont=dict(color="#D1495B", size=13, family="Inter"),
                marker=dict(
                    color=colors,
                    cornerradius=5,
                ),
                width=0.55,
            )
        )
        max_rate = max(plot_df["rate"]) if len(plot_df) > 0 else 50
        fig_drivers.update_layout(
            height=460,
            margin=dict(l=150, r=60, t=10, b=20),
            xaxis=dict(range=[0, max_rate * 1.2], showgrid=True, gridcolor="#EDF0F4", zeroline=False),
            yaxis=dict(showgrid=False, tickfont=dict(size=13, color="#40536B", family="Inter")),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_drivers, width="stretch")

    # Caption ensuring 'These are factors associated with churn, not proven causes.' appears below chart
    st.markdown(
        '<div class="takeaway">These are factors associated with churn, not proven causes.</div>',
        unsafe_allow_html=True,
    )

    render_footer()

# ===========================================================================
# TAB 3: CUSTOMER LIFETIME
# ===========================================================================
with tab3:
    render_banner("Customer lifetime", "Retention over the customer lifetime")

    st.markdown('<p class="section-kicker">Retention curve</p>', unsafe_allow_html=True)
    st.markdown(
        '<h2 style="color: #1f3a5f; margin: 0 0 16px 0; font-size: 20px; font-weight: 700;">Share of customers still active</h2>',
        unsafe_allow_html=True,
    )

    km_df = df[df["tenure"] > 0].copy()

    contract_configs = [
        {"name": "Month-to-month", "color": "#D1495B", "textpos": "bottom center"},
        {"name": "One year", "color": "#2A9D8F", "textpos": "bottom center"},
        {"name": "Two year", "color": "#1F3A5F", "textpos": "top center"},
    ]

    retention_table_rows = []
    fig_km = go.Figure()

    for cfg in contract_configs:
        c_name = cfg["name"]
        color = cfg["color"]
        textpos = cfg["textpos"]
        sub = km_df[km_df["contract"] == c_name]

        if len(sub) == 0:
            continue

        t_list = [0]
        s_list = [100.0]
        S = 1.0

        for t in range(1, 73):
            at_risk = int((sub["tenure"] >= t).sum())
            if at_risk < 100:
                # Stop drawing each curve where at_risk < 100
                break
            events = int(((sub["tenure"] == t) & (sub["churn_flag"] == 1)).sum())
            S = S * (1.0 - (events / at_risk if at_risk > 0 else 0.0))
            t_list.append(t)
            s_list.append(S * 100.0)

        # Draw curve line
        fig_km.add_trace(
            go.Scatter(
                x=t_list,
                y=s_list,
                mode="lines",
                name=c_name,
                line=dict(color=color, width=3.5),
                hoverinfo="x+y+name",
            )
        )

        # Value labels ONLY at months 12, 24, 48, placed so they never overlap
        t_arr = np.array(t_list)
        s_arr = np.array(s_list)
        milestones = [m for m in [12, 24, 48] if m in t_arr]
        m_vals = [s_arr[np.where(t_arr == m)[0][0]] for m in milestones]

        if milestones:
            fig_km.add_trace(
                go.Scatter(
                    x=milestones,
                    y=m_vals,
                    mode="markers+text",
                    marker=dict(size=8, color="#FFFFFF", line=dict(color=color, width=2.5)),
                    text=[f"{v:.1f}%" for v in m_vals],
                    textposition=textpos,
                    textfont=dict(color=color, size=11, family="Inter", weight="bold"),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

        # Milestone table data
        row_dict = {"Contract": c_name}
        for m in [12, 24, 48]:
            if m in t_arr:
                val = s_arr[np.where(t_arr == m)[0][0]]
                row_dict[f"{m} months"] = f"{val:.1f}%"
            else:
                row_dict[f"{m} months"] = "N/A (<100 at risk)"
        retention_table_rows.append(row_dict)

    # Ticks at 0, 12, 24, 36, 48, 60, 72
    fig_km.update_layout(
        height=450,
        margin=dict(l=40, r=40, t=30, b=40),
        xaxis=dict(
            title="Months",
            tickvals=[0, 12, 24, 36, 48, 60, 72],
            showgrid=True,
            gridcolor="#EDF0F4",
            gridwidth=1,
            griddash="dot",
        ),
        yaxis=dict(
            range=[30, 108],
            tickvals=[40, 60, 80, 100],
            tickformat=".0f",
            showgrid=True,
            gridcolor="#EDF0F4",
            gridwidth=1,
            griddash="dot",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color="#5C6D81", family="Inter"),
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
    )
    st.plotly_chart(fig_km, width="stretch")

    # Required caption
    st.markdown(
        '<p style="text-align: center; color: #718096; font-size: 12px; margin-top: -10px;">'
        "Retention estimated from tenure (Kaplan-Meier). Curves stop where fewer than 100 customers remain at risk."
        "</p>",
        unsafe_allow_html=True,
    )

    # Small table of retention at 12, 24, 48 months
    st.write("")
    if retention_table_rows:
        ret_table = pd.DataFrame(retention_table_rows).set_index("Contract")
        st.dataframe(ret_table, width="stretch")

    # -----------------------------------------------------------------------
    # NEW - Cohort view: churn by plan and tenure
    # -----------------------------------------------------------------------
    st.markdown(
        """
        <div style="margin-top: 36px; margin-bottom: 8px;">
          <p class="section-kicker">Cohort view</p>
          <h2 style="color: #1f3a5f; margin: 0 0 8px 0; font-size: 20px; font-weight: 700;">Cohort view: churn by plan and tenure</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    def get_tenure_band_label(t):
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

    df_cohort_base = df.copy()
    df_cohort_base["cohort_tb"] = df_cohort_base["tenure"].map(get_tenure_band_label)

    cohort_contracts = ["Month-to-month", "One year", "Two year"]
    cohort_tb_cols = ["0-6", "7-12", "13-24", "25-48", "49-72"]

    table_rows_html = []
    for c in cohort_contracts:
        cells_html = [f'<td class="row-label">{c}</td>']
        for tb in cohort_tb_cols:
            sub = df_cohort_base[
                (df_cohort_base["contract"] == c) & (df_cohort_base["cohort_tb"] == tb)
            ]
            cust_n = len(sub)
            if cust_n == 0:
                cells_html.append(
                    '<td style="background-color: #f8fafc; color: #94a3b8;">'
                    '<div class="cell-rate">n/a</div>'
                    "</td>"
                )
            else:
                ch_cnt = int(sub["churn_flag"].sum())
                rate = (ch_cnt / cust_n) * 100
                star = "*" if cust_n < 50 else ""

                # Color heatmap: gentle red progression
                alpha = min(0.65, max(0.06, (rate / 60.0) * 0.65))
                bg_color = f"rgba(209, 73, 91, {alpha:.3f})"
                text_color = "#1f3a5f" if rate < 38 else "#ffffff"
                count_color = "#64748b" if rate < 38 else "#f1f5f9"

                cells_html.append(
                    f'<td style="background-color: {bg_color}; color: {text_color};">'
                    f'<div class="cell-rate" style="color: {text_color};">{rate:.1f}%{star}</div>'
                    f'<div class="cell-count" style="color: {count_color};">{cust_n:,} cust.</div>'
                    f"</td>"
                )
        table_rows_html.append("<tr>" + "".join(cells_html) + "</tr>")

    cohort_html = f"""
    <table class="cohort-table">
      <thead>
        <tr>
          <th>Contract</th>
          <th>0–6 mo</th>
          <th>7–12 mo</th>
          <th>13–24 mo</th>
          <th>25–48 mo</th>
          <th>49–72 mo</th>
        </tr>
      </thead>
      <tbody>
        {"".join(table_rows_html)}
      </tbody>
    </table>
    """
    st.markdown(cohort_html, unsafe_allow_html=True)
    st.caption("* small group, interpret with caution")
    st.caption("Tenure-based cohorts by plan; the data has no signup dates or region.")

    render_footer()

# ===========================================================================
# TAB 4: ACTION PLAN
# ===========================================================================
with tab4:
    render_banner("Action plan", "Retention priorities")

    risk_mask = (
        (df["contract"] == "Month-to-month")
        & (df["internet_service"] == "Fiber optic")
        & (df["payment_method"] == "Electronic check")
    )
    seg_df = df[risk_mask]
    seg_count = len(seg_df)
    seg_churn_count = int(seg_df["churn_flag"].sum())
    seg_churn_rate = (seg_churn_count / seg_count * 100) if seg_count > 0 else 0.0
    total_churners = int(df["churn_flag"].sum())
    seg_churn_share = (seg_churn_count / total_churners * 100) if total_churners > 0 else 0.0

    st.markdown(
        f"""
        <article class="risk-callout">
          <span class="risk-label">Highest-risk segment</span>
          <h2>Month-to-month + fiber optic + electronic check</h2>
          <div class="risk-stats">
            <div>
              <strong>{seg_count:,}</strong>
              <span>customers</span>
            </div>
            <div>
              <strong>{seg_churn_rate:.1f}%</strong>
              <span>churn</span>
            </div>
            <div>
              <strong>{seg_churn_share:.1f}%</strong>
              <span>of all churners</span>
            </div>
          </div>
        </article>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="section-kicker">Recommended actions</p>', unsafe_allow_html=True)
    st.markdown(
        '<h2 style="color: #1f3a5f; margin: 0 0 20px 0; font-size: 20px; font-weight: 700;">Five priorities to improve retention</h2>',
        unsafe_allow_html=True,
    )

    recs = [
        "Move new customers to annual contracts",
        "Add a first-6-months onboarding programme",
        "Bundle tech support and online security",
        "Encourage automatic payment methods",
        "Review fiber optic pricing and service quality",
    ]

    # Equal height recommendation cards in each row
    r_col1, r_col2, r_col3 = st.columns(3)
    with r_col1:
        st.markdown(
            f"""
            <div class="rec-card">
              <span class="rec-badge">1</span>
              <h4>{recs[0]}</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with r_col2:
        st.markdown(
            f"""
            <div class="rec-card">
              <span class="rec-badge">2</span>
              <h4>{recs[1]}</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with r_col3:
        st.markdown(
            f"""
            <div class="rec-card">
              <span class="rec-badge">3</span>
              <h4>{recs[2]}</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    r_col4, r_col5 = st.columns(2)
    with r_col4:
        st.markdown(
            f"""
            <div class="rec-card">
              <span class="rec-badge">4</span>
              <h4>{recs[3]}</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with r_col5:
        st.markdown(
            f"""
            <div class="rec-card">
              <span class="rec-badge">5</span>
              <h4>{recs[4]}</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")

    # -----------------------------------------------------------------------
    # NEW - Expander "About this analysis"
    # -----------------------------------------------------------------------
    with st.expander("About this analysis"):
        total_rows = len(df_raw)
        blank_tc_count = 11  # Customers with tenure 0 having blank TotalCharges
        st.markdown(
            f"""
            - **Dataset**: Telco Customer Churn dataset (Kaggle), covering **{total_rows:,} customers** across 21 raw attributes.
            - **Data cleaning**: {blank_tc_count} blank `TotalCharges` values (all customers with tenure 0) were converted to numeric and set to 0.0; no duplicate rows found.
            - **Tools**: Python, pandas, NumPy, Plotly, Streamlit.
            - **Limitations**:
                - Findings are statistical associations with churn, not proof of cause.
                - The data has no signup dates, region or stated churn reasons, so cohorts are tenure-based.
                - Retention curves are less reliable at higher tenures where few customers remain at risk.
                - Single snapshot of cross-sectional customer data without historical contract changes.
            """
        )

    render_footer()
