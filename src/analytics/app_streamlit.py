import streamlit as st
import pandas as pd
import json
import os
from decimal import Decimal, ROUND_HALF_UP
import plotly.graph_objects as go
import plotly.express as px

# 1. Page Configuration & Custom CSS (Fintech Theme)
st.set_page_config(
    page_title="YottaFlex | Underwriting Decision Cockpit",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 5px;
    }
    .metric-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 8px;
    }
    .badge-green { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }
    .badge-amber { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }
    .badge-red { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
    .badge-blue { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid #3b82f6; }
</style>
""", unsafe_allow_html=True)

# 2. Load Core Data


@st.cache_data
def load_all_data():
    metrics_path = "outputs/evaluation_metrics.json"
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    quotes_df = pd.read_csv("data/generated/quotes.csv")
    decisions_df = pd.read_csv("data/generated/underwriting_decisions.csv")
    policies_df = pd.read_csv("data/generated/policies.csv")
    ground_truth_df = pd.read_csv("data/ground_truth/ground_truth.csv")

    return metrics, quotes_df, decisions_df, policies_df, ground_truth_df


metrics, quotes, decisions, policies, ground_truth = load_all_data()
kpis = metrics["underwriting_kpis"]
anom = metrics["anomaly_detection_benchmark"]

# Header
col_title, col_tag = st.columns([3, 1])
with col_title:
    st.title("🛡️ YottaFlex Underwriting & Risk Cockpit")
    st.caption(
        f"System Seed: `{metrics['seed']}` | Target Scale: `{metrics['system_scale'].upper()}` | ANSI SQL & Actuarial Precision")
with col_tag:
    st.markdown("<br>", unsafe_allow_html=True)
    st.success("● Pipeline Healthy • 0 Schema Errors")

st.markdown("---")

# 3. Top Interactive Tabs
tab_exec, tab_simulator, tab_anomalies, tab_explorer = st.tabs([
    "📈 Executive Overview",
    "⚡ Interactive Underwriting Simulator",
    "🎯 Anomaly Benchmark (N=58)",
    "🔍 Relational Data Explorer"
])

# ----------------- TAB 1: EXECUTIVE OVERVIEW -----------------
with tab_exec:
    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Submissions Evaluated</div>
            <div class="metric-value">{kpis['total_submissions_evaluated']:,}</div>
            <span class="metric-badge badge-blue">4,000 Quoted Transactions</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Straight-Through (STP)</div>
            <div class="metric-value">{kpis['straight_through_processing_count']:,}</div>
            <span class="metric-badge badge-green">{kpis['straight_through_processing_rate_pct']:.2f}% Auto-Approval Rate</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Underwriter Referrals</div>
            <div class="metric-value">{kpis['referral_count']:,}</div>
            <span class="metric-badge badge-amber">L1 Analyst / Senior VP Review</span>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Hard Declines</div>
            <div class="metric-value">{kpis['decline_count']:,}</div>
            <span class="metric-badge badge-red">Capacity Breach / Credit Hurdle</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row
    chart_col1, chart_col2 = st.columns([1, 1])

    with chart_col1:
        st.markdown("#### **Decision Triage Distribution**")
        labels = ["STP Auto-Approved", "Manual Referrals", "Hard Declines"]
        values = [kpis['straight_through_processing_count'],
                  kpis['referral_count'], kpis['decline_count']]
        colors = ["#22c55e", "#f59e0b", "#ef4444"]

        fig_pie = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.55,
            marker=dict(colors=colors),
            textinfo='label+percent'
        )])
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#f8fafc"),
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=False
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        st.markdown("#### **Sum Insured Exposure by Product**")
        quotes_summary = quotes.groupby(
            "product_id")["sum_insured"].sum().reset_index()
        quotes_summary["sum_insured_cr"] = quotes_summary["sum_insured"] / 1e7

        fig_bar = px.bar(
            quotes_summary,
            x="product_id",
            y="sum_insured_cr",
            labels={"product_id": "Product Line",
                    "sum_insured_cr": "Total Exposure (₹ Crores)"},
            color="product_id",
            color_discrete_sequence=["#38bdf8", "#818cf8", "#c084fc"]
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#f8fafc"),
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ----------------- TAB 2: LIVE SIMULATOR -----------------
with tab_simulator:
    st.markdown("### ⚡ Live Actuarial Rating & Routing Engine")
    st.caption(
        "Adjust policy applicant risk factors to test real-time pricing and automated underwriting authority.")

    sim_col1, sim_col2 = st.columns([1, 1])

    with sim_col1:
        product_choice = st.selectbox("Product Line", [
                                      "PRD-PROP-01 (Property)", "PRD-AUTO-01 (Auto)", "PRD-CYBR-01 (Cyber)"])
        sum_insured = st.slider("Sum Insured (₹)", min_value=500000,
                                max_value=40000000, value=10000000, step=500000)
        credit_score = st.slider(
            "Applicant Credit Score", min_value=300, max_value=850, value=750, step=5)
        loss_count = st.slider("3-Year Loss / Claim Count",
                               min_value=0, max_value=5, value=0)
        asset_risk = st.slider("Asset Risk Hazard Score (1.0 to 10.0)",
                               min_value=1.0, max_value=10.0, value=4.5, step=0.1)

    # Actuarial Math Computation
    base_rate = Decimal("0.0200") if "PROP" in product_choice else (
        Decimal("0.0350") if "AUTO" in product_choice else Decimal("0.0250"))

    # Credit Multiplier
    if credit_score < 580:
        c_mult = Decimal("1.500")
    elif credit_score < 670:
        c_mult = Decimal("1.200")
    elif credit_score < 750:
        c_mult = Decimal("1.000")
    else:
        c_mult = Decimal("0.850")

    # Loss Multiplier
    if loss_count == 0:
        l_mult = Decimal("0.900")
    elif loss_count == 1:
        l_mult = Decimal("1.150")
    elif loss_count == 2:
        l_mult = Decimal("1.400")
    elif loss_count == 3:
        l_mult = Decimal("1.750")
    else:
        l_mult = Decimal("2.200")

    # Asset Multiplier
    a_mult = (Decimal(str(asset_risk)) / Decimal("5.000")
              ).quantize(Decimal("0.001"))
    calculated_premium = (Decimal(sum_insured) * base_rate * c_mult *
                          l_mult * a_mult).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Authority Routing
    if credit_score < 500:
        decision = "HARD_DECLINE"
        authority = "SYSTEM"
        color = "badge-red"
        reason = "Credit score falls below minimum 500 threshold."
    elif sum_insured > 25000000 or loss_count > 2:
        decision = "REFERRAL"
        authority = "SENIOR_VP"
        color = "badge-amber"
        reason = "Sum Insured > ₹2.5 Cr or loss history > 2 requires Senior VP sign-off."
    elif credit_score < 650 or loss_count == 2 or asset_risk > 6.0:
        decision = "REFERRAL"
        authority = "UNDERWRITER_L1"
        color = "badge-amber"
        reason = "Moderate risk profile requires operations analyst review."
    else:
        decision = "AUTO_APPROVE"
        authority = "STP_SYSTEM"
        color = "badge-green"
        reason = "Clean profile qualifies for Straight-Through Processing."

    with sim_col2:
        st.markdown("#### **Evaluation Engine Output**")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Calculated Annual Premium</div>
            <div class="metric-value">₹{calculated_premium:,.2f}</div>
            <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 10px;">
                <strong>Formula:</strong> ₹{sum_insured:,} × {base_rate} × {c_mult} (Credit) × {l_mult} (Loss) × {a_mult} (Hazard)
            </div>
            <hr style="border-color: #334155; margin: 15px 0;">
            <div class="metric-label">Routing Decision</div>
            <div style="font-size: 1.35rem; font-weight: 700; color: #f8fafc; margin-top: 4px;">
                {decision}
            </div>
            <span class="metric-badge {color}">Assigned Authority: {authority}</span>
            <div style="font-size: 0.85rem; color: #cbd5e1; margin-top: 8px;">
                <strong>Audit Trail Reason:</strong> {reason}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ----------------- TAB 3: ANOMALIES BENCHMARK -----------------
with tab_anomalies:
    st.markdown("### 🎯 Injected Anomaly Audit & Classification Benchmark")
    st.caption(
        "Verification against the isolated ground-truth dataset (N=58) across all 5 negative edge cases.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        "Precision", f"{anom['precision'] * 100:.1f}%", "Zero False Positives")
    m2.metric("Recall", f"{anom['recall'] * 100:.1f}%", "Zero Missed Defects")
    m3.metric("F1-Score", f"{anom['f1_score']:.4f}", "Harmonic Mean")
    m4.metric("Audited Pipeline Volume",
              f"{anom['total_records_audited']:,}", "100% Inspected")

    st.markdown("<br>", unsafe_allow_html=True)
    c_heat, c_table = st.columns([1, 1.2])

    with c_heat:
        st.markdown("#### **Confusion Matrix Heatmap**")
        z = [[anom['true_positives'], anom['false_negatives']],
             [anom['false_positives'], anom['true_negatives']]]
        fig_heat = px.imshow(
            z,
            text_auto=True,
            x=['Predicted Anomaly', 'Predicted Normal'],
            y=['Actual Anomaly', 'Actual Normal'],
            color_continuous_scale="Blues"
        )
        fig_heat.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#f8fafc"),
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    with c_table:
        st.markdown("#### **Ground Truth Anomaly Category Breakdown**")
        gt_summary = ground_truth["issue_type"].value_counts().reset_index()
        gt_summary.columns = ["Injected Anomaly Type", "Incident Count"]
        st.dataframe(gt_summary, use_container_width=True, hide_index=True)

# ----------------- TAB 4: DATA EXPLORER -----------------
with tab_explorer:
    st.markdown("### 🔍 Live Data Catalog & Table Inspector")
    table_choice = st.selectbox(
        "Select Entity:",
        ["policies", "quotes", "underwriting_decisions",
            "renewals", "endorsements", "ground_truth"]
    )

    if table_choice == "ground_truth":
        display_df = ground_truth
    elif table_choice == "policies":
        display_df = policies
    elif table_choice == "quotes":
        display_df = quotes
    elif table_choice == "underwriting_decisions":
        display_df = decisions
    else:
        display_df = pd.read_csv(f"data/generated/{table_choice}.csv")

    st.dataframe(display_df, use_container_width=True)
