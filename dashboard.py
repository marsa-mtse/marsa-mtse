import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="MTSE Intelligence",
    page_icon="📊",
    layout="wide"
)

# ===============================
# CUSTOM STYLING (Premium Dark)
# ===============================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: rgba(20, 30, 40, 0.95);
}

h1, h2, h3 {
    color: #ffffff;
}

.stMetric {
    background-color: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 MTSE Intelligence Platform")
st.markdown("### AI Marketing Analytics System")

# ===============================
# FILE UPLOAD
# ===============================
uploaded_file = st.file_uploader(
    "📂 Upload Campaign CSV File",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    # ===============================
    # CLEAN COLUMN NAMES
    # ===============================
    df.columns = df.columns.str.strip().str.lower()

    required_cols = ["campaign", "impressions", "clicks", "spend", "revenue"]

    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ CSV must contain columns: {required_cols}")
        st.stop()

    # ===============================
    # SAFE NUMERIC CONVERSION
    # ===============================
    for col in ["impressions", "clicks", "spend", "revenue"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ===============================
    # AI METRICS CALCULATION
    # ===============================
    df["ctr"] = np.where(df["impressions"] > 0,
                         df["clicks"] / df["impressions"], 0)

    df["cpc"] = np.where(df["clicks"] > 0,
                         df["spend"] / df["clicks"], 0)

    df["roas"] = np.where(df["spend"] > 0,
                          df["revenue"] / df["spend"], 0)

    # ===============================
    # GLOBAL KPIs
    # ===============================
    total_spend = df["spend"].sum()
    total_revenue = df["revenue"].sum()
    total_clicks = df["clicks"].sum()
    total_impressions = df["impressions"].sum()

    overall_roas = total_revenue / total_spend if total_spend > 0 else 0
    overall_ctr = total_clicks / total_impressions if total_impressions > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Total Spend", f"${total_spend:,.0f}")
    col2.metric("📈 Total Revenue", f"${total_revenue:,.0f}")
    col3.metric("🎯 Overall ROAS", f"{overall_roas:.2f}")
    col4.metric("📊 Overall CTR", f"{overall_ctr:.2%}")

    st.divider()

    # ===============================
    # PERFORMANCE CHARTS
    # ===============================
    st.subheader("📊 Revenue by Campaign")
    fig1 = px.bar(df, x="campaign", y="revenue", color="campaign")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📊 ROAS by Campaign")
    fig2 = px.bar(df, x="campaign", y="roas", color="campaign")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📊 CTR by Campaign")
    fig3 = px.bar(df, x="campaign", y="ctr", color="campaign")
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ===============================
    # AI SMART ANALYSIS
    # ===============================
    st.subheader("🤖 AI Strategic Insights")

    best_roas_campaign = df.loc[df["roas"].idxmax()]
    worst_roas_campaign = df.loc[df["roas"].idxmin()]

    st.success(
        f"🔥 Best Campaign: {best_roas_campaign['campaign']} "
        f"(ROAS: {best_roas_campaign['roas']:.2f})"
    )

    st.warning(
        f"⚠ Weak Campaign: {worst_roas_campaign['campaign']} "
        f"(ROAS: {worst_roas_campaign['roas']:.2f})"
    )

    # Budget Optimization Suggestion
    high_performers = df[df["roas"] > overall_roas]

    if not high_performers.empty:
        recommended_budget_shift = high_performers["campaign"].tolist()
        st.info(
            f"📌 Recommendation: Shift more budget toward: {recommended_budget_shift}"
        )

    # ===============================
    # DOWNLOAD REPORT
    # ===============================
    st.subheader("📥 Download Enhanced Report")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Full Analysis CSV",
        csv,
        "mtse_analysis_report.csv",
        "text/csv"
    )

else:
    st.info("Upload a CSV file to begin analysis.")
