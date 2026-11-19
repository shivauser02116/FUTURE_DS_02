#!/usr/bin/env python3
"""
scripts/02_build_dashboard.py
=============================
Generates a 4-page executive dashboard for FUTURE_DS_02 (Telco Customer Churn):
  - Page 1: Overview (KPIs, Churn by Contract, Churn by Tenure Band)
  - Page 2: Churn Drivers (Ranked factor bars, disclaimer)
  - Page 3: Customer Lifetime (Kaplan-Meier survival curves, milestone table, cohort heatmap)
  - Page 4: Action Plan (Highest-risk segment callout, 5 recommendations, limitations)

Output artifacts:
  - dashboard/FUTURE_DS_02_dashboard.pdf (multi-page 16:9 PDF)
  - images/page_1.png
  - images/page_2.png
  - images/page_3.png
  - images/page_4.png

Palette:
  - Navy: #1F3A5F
  - Teal: #2A9D8F
  - Red:  #D1495B
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

# Set matplotlib cache to writable directory before importing pyplot
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle

# ---------------------------------------------------------------------------
# Setup paths & styling constants
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "telco_clean.csv"
DASHBOARD_DIR = REPO_ROOT / "dashboard"
IMAGES_DIR = REPO_ROOT / "images"

DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

PDF_OUTPUT = DASHBOARD_DIR / "FUTURE_DS_02_dashboard.pdf"

# Design Tokens (16:9 aspect ratio)
FIG_WIDTH = 16.0
FIG_HEIGHT = 9.0
DPI = 150

COLOR_NAVY = "#1F3A5F"
COLOR_NAVY_LIGHT = "#2B4C7E"
COLOR_TEAL = "#2A9D8F"
COLOR_RED = "#D1495B"
COLOR_RED_LIGHT = "#E87A88"
COLOR_BG = "#F8FAFC"
COLOR_CARD_BG = "#FFFFFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT_MAIN = "#1E293B"
COLOR_TEXT_MUTED = "#64748B"
COLOR_GRID = "#F1F5F9"

FOOTER_TEXT = "Source: Telco Customer Churn dataset (Kaggle). Analysis in FUTURE_DS_02."


# ---------------------------------------------------------------------------
# Helper Layout Functions
# ---------------------------------------------------------------------------
def setup_page(eyebrow: str, title: str, headline: str):
    """Creates a base 16:9 figure with header banner and footer."""
    fig = plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT), facecolor=COLOR_BG)
    
    # Header banner ax (top coordinates in figure fraction [0, 1])
    # Top 13% for banner
    banner_ax = fig.add_axes([0.0, 0.87, 1.0, 0.13], facecolor=COLOR_NAVY)
    banner_ax.set_xticks([])
    banner_ax.set_yticks([])
    for spine in banner_ax.spines.values():
        spine.set_visible(False)
        
    banner_ax.text(
        0.04, 0.72, eyebrow.upper(),
        color="#A9DED7", fontsize=10, fontweight="bold",
        va="center", ha="left"
    )
    banner_ax.text(
        0.04, 0.38, title,
        color="#FFFFFF", fontsize=19, fontweight="bold",
        va="center", ha="left"
    )
    banner_ax.text(
        0.96, 0.38, headline,
        color="#E2E8F0", fontsize=11, fontstyle="italic",
        va="center", ha="right"
    )

    # Footer
    fig.text(
        0.5, 0.02, FOOTER_TEXT,
        color=COLOR_TEXT_MUTED, fontsize=10,
        ha="center", va="center"
    )
    
    return fig


def draw_card(ax, rect, title, value, subtitle="", border_color=COLOR_BORDER, val_color=COLOR_NAVY):
    """Draws a clean styled KPI card in axes coordinates."""
    x, y, w, h = rect
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=COLOR_CARD_BG,
        edgecolor=border_color,
        linewidth=1.2,
        zorder=2
    )
    ax.add_patch(box)
    
    # Title
    ax.text(
        x + w * 0.08, y + h * 0.76, title.upper(),
        color=COLOR_TEXT_MUTED, fontsize=8.5, fontweight="bold",
        va="center", ha="left", zorder=3
    )
    # Value
    ax.text(
        x + w * 0.08, y + h * 0.45, value,
        color=val_color, fontsize=18, fontweight="bold",
        va="center", ha="left", zorder=3
    )
    # Subtitle
    if subtitle:
        ax.text(
            x + w * 0.08, y + h * 0.18, subtitle,
            color=COLOR_TEXT_MUTED, fontsize=8.5,
            va="center", ha="left", zorder=3
        )


# ---------------------------------------------------------------------------
# Page 1: Overview
# ---------------------------------------------------------------------------
def build_page_1(df: pd.DataFrame):
    n_cust = len(df)
    n_churn = int(df["churn_flag"].sum())
    churn_rate = (n_churn / n_cust * 100) if n_cust > 0 else 0.0
    
    total_mrr = df["monthly_charges"].sum()
    churn_mrr = df[df["churn_flag"] == 1]["monthly_charges"].sum()
    mrr_share = (churn_mrr / total_mrr * 100) if total_mrr > 0 else 0.0
    
    churned_df = df[df["churn_flag"] == 1]
    retained_df = df[df["churn_flag"] == 0]
    avg_chg_churn = churned_df["monthly_charges"].mean()
    avg_chg_ret = retained_df["monthly_charges"].mean()
    avg_ten_churn = churned_df["tenure"].mean()
    avg_ten_ret = retained_df["tenure"].mean()

    fig = setup_page(
        eyebrow="Executive Overview | Telco Customer Churn",
        title="Customer Retention & Churn Overview",
        headline=f"Overall Churn: {churn_rate:.1f}% | Monthly Revenue Lost: ${churn_mrr/1e3:.0f}K ({mrr_share:.1f}% of total)"
    )

    # 1. KPI Cards container
    kpi_ax = fig.add_axes([0.04, 0.53, 0.92, 0.30], facecolor=COLOR_BG)
    kpi_ax.set_xticks([])
    kpi_ax.set_yticks([])
    for spine in kpi_ax.spines.values():
        spine.set_visible(False)

    card_defs = [
        ("Customers", f"{n_cust:,}", "Total active accounts", COLOR_NAVY),
        ("Churn Rate", f"{churn_rate:.1f}%", f"{n_churn:,} accounts churned", COLOR_RED),
        ("Churned Customers", f"{n_churn:,}", f"{(100-churn_rate):.1f}% retained", COLOR_RED),
        ("Monthly Revenue Lost", f"${churn_mrr/1e3:.0f}K", f"{mrr_share:.1f}% of ${total_mrr/1e3:.0f}K MRR", COLOR_RED),
        ("Avg Monthly Charge", f"${avg_chg_churn:.2f}", f"churned vs ${avg_chg_ret:.2f} retained", COLOR_NAVY),
        ("Avg Tenure", f"{avg_ten_churn:.1f} mos", f"churned vs {avg_ten_ret:.1f} mos retained", COLOR_NAVY),
    ]

    # 2 rows x 3 columns of cards
    for idx, (lbl, val, sub, col) in enumerate(card_defs):
        row = idx // 3
        col_idx = idx % 3
        cx = col_idx * 0.34
        cy = 0.52 - row * 0.48
        cw = 0.32
        ch = 0.44
        draw_card(kpi_ax, (cx, cy, cw, ch), lbl, val, sub, val_color=col)

    # 2. Left Chart: Churn by Contract
    ax_contract = fig.add_axes([0.06, 0.10, 0.40, 0.37], facecolor=COLOR_CARD_BG)
    for s in ["top", "right"]:
        ax_contract.spines[s].set_visible(False)
    ax_contract.spines["left"].set_color(COLOR_BORDER)
    ax_contract.spines["bottom"].set_color(COLOR_BORDER)

    c_order = ["Month-to-month", "One year", "Two year"]
    c_rates = [df[df["contract"] == c]["churn_flag"].mean() * 100 for c in c_order]
    bars_c = ax_contract.bar(c_order, c_rates, color=[COLOR_RED, COLOR_TEAL, COLOR_NAVY], width=0.48)
    ax_contract.set_title("Churn Rate by Contract Type", fontsize=13, fontweight="bold", color=COLOR_NAVY, pad=14, loc="left")
    ax_contract.set_ylim(0, 52)
    ax_contract.set_ylabel("Churn Rate (%)", color=COLOR_TEXT_MUTED, fontsize=10)
    ax_contract.grid(axis="y", color=COLOR_GRID, linestyle="--", alpha=0.7)
    ax_contract.tick_params(colors=COLOR_TEXT_MAIN, labelsize=10)

    for bar, rate in zip(bars_c, c_rates):
        yval = bar.get_height()
        ax_contract.text(
            bar.get_x() + bar.get_width() / 2.0, yval + 1.2,
            f"{rate:.1f}%", ha="center", va="bottom",
            fontsize=11, fontweight="bold", color=COLOR_TEXT_MAIN
        )

    # 3. Right Chart: Churn by Tenure Band
    ax_tenure = fig.add_axes([0.54, 0.10, 0.42, 0.37], facecolor=COLOR_CARD_BG)
    for s in ["top", "right"]:
        ax_tenure.spines[s].set_visible(False)
    ax_tenure.spines["left"].set_color(COLOR_BORDER)
    ax_tenure.spines["bottom"].set_color(COLOR_BORDER)

    def get_tenure_band(t):
        if t <= 6: return "0-6"
        elif t <= 12: return "7-12"
        elif t <= 24: return "13-24"
        elif t <= 48: return "25-48"
        else: return "49-72"

    df_tb = df.copy()
    df_tb["tb_calc"] = df_tb["tenure"].map(get_tenure_band)
    tb_order = ["0-6", "7-12", "13-24", "25-48", "49-72"]
    tb_display = ["0–6 mo", "7–12 mo", "13–24 mo", "25–48 mo", "49–72 mo"]
    tb_rates = [df_tb[df_tb["tb_calc"] == b]["churn_flag"].mean() * 100 for b in tb_order]
    
    tb_colors = [COLOR_RED, COLOR_RED_LIGHT, "#E5A93C", COLOR_TEAL, COLOR_NAVY]
    bars_t = ax_tenure.bar(tb_display, tb_rates, color=tb_colors, width=0.52)
    ax_tenure.set_title("Churn Rate by Tenure Band", fontsize=13, fontweight="bold", color=COLOR_NAVY, pad=14, loc="left")
    ax_tenure.set_ylim(0, 62)
    ax_tenure.set_ylabel("Churn Rate (%)", color=COLOR_TEXT_MUTED, fontsize=10)
    ax_tenure.grid(axis="y", color=COLOR_GRID, linestyle="--", alpha=0.7)
    ax_tenure.tick_params(colors=COLOR_TEXT_MAIN, labelsize=10)

    for bar, rate in zip(bars_t, tb_rates):
        yval = bar.get_height()
        ax_tenure.text(
            bar.get_x() + bar.get_width() / 2.0, yval + 1.2,
            f"{rate:.1f}%", ha="center", va="bottom",
            fontsize=11, fontweight="bold", color=COLOR_TEXT_MAIN
        )

    return fig


# ---------------------------------------------------------------------------
# Page 2: Churn Drivers
# ---------------------------------------------------------------------------
def build_page_2(df: pd.DataFrame):
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
        rate = subset["churn_flag"].mean() * 100
        count = len(subset)
        driver_rows.append({"label": label, "rate": rate, "count": count})

    driver_df = pd.DataFrame(driver_rows).sort_values("rate", ascending=True).reset_index(drop=True)
    overall_churn = df["churn_flag"].mean() * 100

    fig = setup_page(
        eyebrow="Churn Drivers | Risk Factor Analysis",
        title="Factors Associated with Customer Churn",
        headline=f"Top Driver: Electronic Check ({driver_df.iloc[-1]['rate']:.1f}% churn) vs Benchmark ({overall_churn:.1f}%)"
    )

    ax = fig.add_axes([0.16, 0.16, 0.76, 0.65], facecolor=COLOR_CARD_BG)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(COLOR_BORDER)
    ax.spines["bottom"].set_color(COLOR_BORDER)

    y_pos = np.arange(len(driver_df))
    # Top 4 factors (rates >= 40%) colored in red, others in teal/navy
    bar_colors = [COLOR_RED if r >= 40.0 else COLOR_TEAL for r in driver_df["rate"]]

    bars = ax.barh(y_pos, driver_df["rate"], color=bar_colors, height=0.58)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(driver_df["label"], fontsize=11, fontweight="600", color=COLOR_TEXT_MAIN)
    ax.set_xlabel("Churn Rate (%)", color=COLOR_TEXT_MUTED, fontsize=11, labelpad=8)
    ax.set_xlim(0, 52)
    ax.grid(axis="x", color=COLOR_GRID, linestyle="--", alpha=0.7)
    ax.tick_params(colors=COLOR_TEXT_MAIN, labelsize=10)

    # Baseline overall churn line
    ax.axvline(overall_churn, color=COLOR_NAVY, linestyle="--", linewidth=1.5, alpha=0.85, zorder=3)
    ax.text(
        overall_churn + 0.6, len(driver_df) - 0.5,
        f"Overall Churn: {overall_churn:.1f}%",
        color=COLOR_NAVY, fontsize=10, fontweight="bold", va="center"
    )

    for bar, row in zip(bars, driver_df.itertuples()):
        w = bar.get_width()
        ax.text(
            w + 0.8, bar.get_y() + bar.get_height() / 2.0,
            f"{row.rate:.1f}%  (n={row.count:,})",
            va="center", ha="left", fontsize=10, fontweight="bold", color=COLOR_TEXT_MAIN
        )

    # Caption box
    fig.text(
        0.5, 0.08,
        "These are factors associated with churn, not proven causes.",
        ha="center", va="center", fontsize=11, fontstyle="italic",
        color=COLOR_NAVY,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#EBF4F6", edgecolor="#A9DED7", linewidth=1.0)
    )

    return fig


# ---------------------------------------------------------------------------
# Page 3: Customer Lifetime
# ---------------------------------------------------------------------------
def build_page_3(df: pd.DataFrame):
    fig = setup_page(
        eyebrow="Customer Lifetime | Survival & Cohort Analysis",
        title="Retention Curves & Cohort Retention by Contract",
        headline="Month-to-month retention drops to 70.3% at 12 mos; 1-yr and 2-yr exceed 90%+ retention"
    )

    # 1. Left: Kaplan-Meier Curves
    ax_km = fig.add_axes([0.06, 0.16, 0.44, 0.65], facecolor=COLOR_CARD_BG)
    for s in ["top", "right"]:
        ax_km.spines[s].set_visible(False)
    ax_km.spines["left"].set_color(COLOR_BORDER)
    ax_km.spines["bottom"].set_color(COLOR_BORDER)

    km_df = df[df["tenure"] > 0]
    contract_configs = [
        {"name": "Month-to-month", "color": COLOR_RED, "ls": "-"},
        {"name": "One year", "color": COLOR_TEAL, "ls": "-"},
        {"name": "Two year", "color": COLOR_NAVY, "ls": "-"},
    ]

    ret_milestones = {}

    for cfg in contract_configs:
        c_name = cfg["name"]
        color = cfg["color"]
        sub = km_df[km_df["contract"] == c_name]
        
        t_list = [0]
        s_list = [100.0]
        S = 1.0

        for t in range(1, 73):
            at_risk = int((sub["tenure"] >= t).sum())
            if at_risk < 100:
                break
            events = int(((sub["tenure"] == t) & (sub["churn_flag"] == 1)).sum())
            S = S * (1.0 - (events / at_risk if at_risk > 0 else 0.0))
            t_list.append(t)
            s_list.append(S * 100.0)

        ax_km.plot(t_list, s_list, label=c_name, color=color, linewidth=2.8, linestyle=cfg["ls"])
        
        # Markers and labels at 12, 24, 48
        t_arr = np.array(t_list)
        s_arr = np.array(s_list)
        m_vals = {}
        for m in [12, 24, 48]:
            if m in t_arr:
                val = s_arr[np.where(t_arr == m)[0][0]]
                m_vals[m] = val
                ax_km.plot(m, val, "o", color=color, markersize=6, markeredgecolor="#FFFFFF", markeredgewidth=1.5)
                # Label positioning
                y_offset = -4.5 if c_name == "Month-to-month" else (-4.0 if c_name == "One year" else 3.2)
                x_offset = 1.0 if c_name == "Month-to-month" else 0.0
                ax_km.text(
                    m + x_offset, val + y_offset, f"{val:.1f}%",
                    fontsize=9, fontweight="bold", color=color, ha="center"
                )
        ret_milestones[c_name] = m_vals

    ax_km.set_title("Kaplan-Meier Retention by Contract", fontsize=13, fontweight="bold", color=COLOR_NAVY, pad=12, loc="left")
    ax_km.set_xlabel("Tenure (Months)", color=COLOR_TEXT_MUTED, fontsize=10, labelpad=6)
    ax_km.set_ylabel("Retention Rate (%)", color=COLOR_TEXT_MUTED, fontsize=10)
    ax_km.set_xlim(-2, 74)
    ax_km.set_ylim(30, 106)
    ax_km.set_xticks([0, 12, 24, 36, 48, 60, 72])
    ax_km.grid(True, color=COLOR_GRID, linestyle="--", alpha=0.7)
    ax_km.tick_params(colors=COLOR_TEXT_MAIN, labelsize=9.5)
    ax_km.legend(loc="lower left", frameon=True, facecolor="#FFFFFF", edgecolor=COLOR_BORDER, fontsize=9.5)

    # Caption directly below KM chart
    fig.text(
        0.28, 0.09,
        "Retention estimated from tenure (Kaplan-Meier). Curves stop where fewer than 100 customers remain at risk.",
        ha="center", va="center", fontsize=8.5, fontstyle="italic", color=COLOR_TEXT_MUTED
    )

    # 2. Right Top: Milestone Retention Table
    ax_tab = fig.add_axes([0.56, 0.58, 0.40, 0.23], facecolor=COLOR_CARD_BG)
    ax_tab.set_xticks([])
    ax_tab.set_yticks([])
    for s in ax_tab.spines.values():
        s.set_visible(False)

    col_labels = ["Contract", "12 Months", "24 Months", "48 Months"]
    table_data = []
    for c_name in ["Month-to-month", "One year", "Two year"]:
        mv = ret_milestones.get(c_name, {})
        table_data.append([
            c_name,
            f"{mv.get(12, 0.0):.1f}%",
            f"{mv.get(24, 0.0):.1f}%",
            f"{mv.get(48, 0.0):.1f}%"
        ])

    table = ax_tab.table(
        cellText=table_data,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
        colColours=[COLOR_NAVY]*4
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.0, 1.8)

    # Style table header text to white
    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_text_props(color="#FFFFFF", weight="bold")
            cell.set_facecolor(COLOR_NAVY)
        else:
            cell.set_facecolor("#FFFFFF" if r % 2 == 1 else "#F8FAFC")
            cell.set_edgecolor(COLOR_BORDER)
            if c == 0:
                cell.set_text_props(weight="bold", color=COLOR_TEXT_MAIN)
            else:
                cell.set_text_props(color=COLOR_TEXT_MAIN)

    ax_tab.set_title("Milestone Retention Summary", fontsize=12, fontweight="bold", color=COLOR_NAVY, pad=8, loc="left")

    # 3. Right Bottom: Cohort Heatmap
    ax_heat = fig.add_axes([0.56, 0.16, 0.40, 0.35], facecolor=COLOR_CARD_BG)
    
    def get_tenure_band(t):
        if t <= 6: return "0-6"
        elif t <= 12: return "7-12"
        elif t <= 24: return "13-24"
        elif t <= 48: return "25-48"
        else: return "49-72"

    df_c = df.copy()
    df_c["tb_calc"] = df_c["tenure"].map(get_tenure_band)
    cohort_contracts = ["Month-to-month", "One year", "Two year"]
    cohort_tbs = ["0-6", "7-12", "13-24", "25-48", "49-72"]
    cohort_tb_labels = ["0–6 mo", "7–12 mo", "13–24 mo", "25–48 mo", "49–72 mo"]

    matrix_rates = np.zeros((3, 5))
    matrix_counts = np.zeros((3, 5), dtype=int)

    for i, c in enumerate(cohort_contracts):
        for j, tb in enumerate(cohort_tbs):
            sub = df_c[(df_c["contract"] == c) & (df_c["tb_calc"] == tb)]
            cnt = len(sub)
            matrix_counts[i, j] = cnt
            matrix_rates[i, j] = (sub["churn_flag"].mean() * 100) if cnt > 0 else 0.0

    im = ax_heat.imshow(matrix_rates, cmap="Reds", aspect="auto", vmin=0, vmax=60)
    
    ax_heat.set_xticks(np.arange(5))
    ax_heat.set_yticks(np.arange(3))
    ax_heat.set_xticklabels(cohort_tb_labels, fontsize=9.5, fontweight="600", color=COLOR_TEXT_MAIN)
    ax_heat.set_yticklabels(cohort_contracts, fontsize=9.5, fontweight="600", color=COLOR_TEXT_MAIN)
    ax_heat.set_title("Cohort View: Churn Rate by Plan & Tenure", fontsize=12, fontweight="bold", color=COLOR_NAVY, pad=8, loc="left")

    for i in range(3):
        for j in range(5):
            rate = matrix_rates[i, j]
            cnt = matrix_counts[i, j]
            star = "*" if cnt < 50 else ""
            txt_color = "#FFFFFF" if rate >= 35.0 else COLOR_TEXT_MAIN
            ax_heat.text(
                j, i - 0.12, f"{rate:.1f}%{star}",
                ha="center", va="center", color=txt_color, fontsize=10, fontweight="bold"
            )
            ax_heat.text(
                j, i + 0.22, f"n={cnt:,}",
                ha="center", va="center", color=txt_color, fontsize=8
            )

    # Cohort footnote and caption
    fig.text(
        0.76, 0.09,
        "* small group (<50 cust.), interpret with caution.  Tenure-based cohorts by plan; the data has no signup dates or region.",
        ha="center", va="center", fontsize=8.5, fontstyle="italic", color=COLOR_TEXT_MUTED
    )

    return fig


# ---------------------------------------------------------------------------
# Page 4: Action Plan
# ---------------------------------------------------------------------------
def build_page_4(df: pd.DataFrame):
    risk_mask = (
        (df["contract"] == "Month-to-month")
        & (df["internet_service"] == "Fiber optic")
        & (df["payment_method"] == "Electronic check")
    )
    seg_df = df[risk_mask]
    seg_cnt = len(seg_df)
    seg_churn_cnt = int(seg_df["churn_flag"].sum())
    seg_rate = (seg_churn_cnt / seg_cnt * 100) if seg_cnt > 0 else 0.0
    total_churners = int(df["churn_flag"].sum())
    seg_share = (seg_churn_cnt / total_churners * 100) if total_churners > 0 else 0.0

    fig = setup_page(
        eyebrow="Strategic Priorities | Retention Roadmap",
        title="Retention Priorities & Highest-Risk Segment",
        headline=f"Highest Risk: 1,307 customers with 60.4% churn represent 42.2% of all churners"
    )

    # 1. Top Callout Card: Highest-Risk Segment
    callout_ax = fig.add_axes([0.06, 0.65, 0.88, 0.18], facecolor=COLOR_NAVY)
    callout_ax.set_xticks([])
    callout_ax.set_yticks([])
    for s in callout_ax.spines.values():
        s.set_visible(False)

    callout_ax.text(
        0.04, 0.80, "HIGHEST-RISK SEGMENT IDENTIFIED",
        color="#A9DED7", fontsize=10, fontweight="bold", va="center"
    )
    callout_ax.text(
        0.04, 0.45, "Month-to-month  +  Fiber optic  +  Electronic check",
        color="#FFFFFF", fontsize=16, fontweight="bold", va="center"
    )

    # Stats on the right side of the callout
    stats = [
        (f"{seg_cnt:,}", "customers"),
        (f"{seg_rate:.1f}%", "churn rate"),
        (f"{seg_share:.1f}%", "of all churners"),
    ]
    for idx, (val, lbl) in enumerate(stats):
        bx = 0.52 + idx * 0.16
        callout_ax.text(bx, 0.58, val, color="#FFFFFF", fontsize=18, fontweight="bold", ha="center", va="center")
        callout_ax.text(bx, 0.28, lbl, color="#CBD5E1", fontsize=9.5, ha="center", va="center")

    # 2. Bottom Left: Five Recommendations
    recs_ax = fig.add_axes([0.06, 0.10, 0.52, 0.51], facecolor=COLOR_CARD_BG)
    recs_ax.set_xticks([])
    recs_ax.set_yticks([])
    for s in recs_ax.spines.values():
        s.set_color(COLOR_BORDER)

    recs_ax.text(
        0.05, 0.94, "RECOMMENDED ACTIONS (5 PRIORITIES TO TEST)",
        fontsize=11, fontweight="bold", color=COLOR_NAVY, va="center"
    )

    recs = [
        ("1", "Move new customers to annual contracts", "Test contract incentives; 1-yr/2-yr churn is 11.3%/2.8% vs 42.7% month-to-month."),
        ("2", "Add a first-6-months onboarding programme", "Early tenure hazard is acute (52.9% churn in months 0-6); test proactive check-ins."),
        ("3", "Bundle tech support and online security", "Support reduces churn from 41.6% to 15.2%; test complimentary 90-day support bundles."),
        ("4", "Encourage automatic payment methods", "Electronic check churn is 45.3% vs ~16% for auto-pay; test $3-$5 monthly auto-pay billing credit."),
        ("5", "Review fiber optic pricing and service quality", "Fiber churn is 41.9% at $91/mo vs DSL 19.0%; audit network reliability and price satisfaction."),
    ]

    for idx, (num, headline_txt, detail_txt) in enumerate(recs):
        y_pos = 0.80 - idx * 0.165
        # Badge circle
        recs_ax.text(
            0.05, y_pos, f"[{num}]",
            fontsize=11, fontweight="bold", color=COLOR_TEAL, va="center"
        )
        recs_ax.text(
            0.11, y_pos + 0.03, headline_txt,
            fontsize=10.5, fontweight="bold", color=COLOR_NAVY, va="center"
        )
        recs_ax.text(
            0.11, y_pos - 0.035, detail_txt,
            fontsize=9, color=COLOR_TEXT_MUTED, va="center"
        )

    # 3. Bottom Right: Limitations Box
    lim_ax = fig.add_axes([0.61, 0.10, 0.33, 0.51], facecolor=COLOR_CARD_BG)
    lim_ax.set_xticks([])
    lim_ax.set_yticks([])
    for s in lim_ax.spines.values():
        s.set_color(COLOR_BORDER)

    lim_ax.text(
        0.08, 0.94, "ANALYSIS LIMITATIONS",
        fontsize=11, fontweight="bold", color=COLOR_NAVY, va="center"
    )

    limits = [
        ("Statistical associations, not causes", "Observed correlations do not prove causality; unobserved factors (service quality, income) may drive both choices and churn."),
        ("Tenure-based cohorts", "The dataset lacks signup dates, geographic region, and stated reasons for cancellation; cohorts reflect accumulated tenure."),
        ("Survival curve tail uncertainty", "Kaplan-Meier retention curves are less reliable at higher tenures where fewer than 100 customers remain at risk."),
        ("Cross-sectional snapshot", "Single snapshot of customer state without longitudinal tracking of plan upgrades or mid-contract behavior changes."),
    ]

    for idx, (head, body) in enumerate(limits):
        y_pos = 0.80 - idx * 0.20
        lim_ax.text(
            0.08, y_pos + 0.03, f"• {head}",
            fontsize=10, fontweight="bold", color=COLOR_TEXT_MAIN, va="center"
        )
        lim_ax.text(
            0.08, y_pos - 0.04, body,
            fontsize=8.5, color=COLOR_TEXT_MUTED, va="center", wrap=True
        )

    return fig


# ---------------------------------------------------------------------------
# Main build entrypoint
# ---------------------------------------------------------------------------
def main():
    print(f"Loading clean dataset from {DATA_PATH}...")
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing input data file: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df):,} customer records.")

    print("\nGenerating dashboard pages...")
    fig1 = build_page_1(df)
    fig2 = build_page_2(df)
    fig3 = build_page_3(df)
    fig4 = build_page_4(df)

    pages = [
        (fig1, IMAGES_DIR / "page_1.png"),
        (fig2, IMAGES_DIR / "page_2.png"),
        (fig3, IMAGES_DIR / "page_3.png"),
        (fig4, IMAGES_DIR / "page_4.png"),
    ]

    print(f"\nWriting multi-page PDF to {PDF_OUTPUT}...")
    with PdfPages(PDF_OUTPUT) as pdf:
        for idx, (fig, img_path) in enumerate(pages, 1):
            pdf.savefig(fig, dpi=DPI, facecolor=fig.get_facecolor(), edgecolor="none")
            fig.savefig(img_path, dpi=DPI, facecolor=fig.get_facecolor(), edgecolor="none")
            print(f"  ✓ Saved Page {idx} -> {img_path.name}")
            plt.close(fig)

    print(f"\n✓ Dashboard generation complete! PDF: {PDF_OUTPUT}")


if __name__ == "__main__":
    main()
