import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="MTSE Intelligence X", layout="wide")

st.title("🚀 MTSE Intelligence X")
st.markdown("### AI Marketing & Growth Intelligence System")

mode = st.radio("اختر النظام", [
    "📊 Ad Performance Intelligence",
    "🔮 Campaign Predictor",
    "📱 Social Growth Analyzer"
])

# ====================================================
# 📊 AD PERFORMANCE INTELLIGENCE
# ====================================================

if mode == "📊 Ad Performance Intelligence":

    file = st.file_uploader("Upload Ads CSV", type=["csv"])

    if file:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.lower()

        rename_map = {
            "ad_name": "campaign",
            "amount_spent": "spend",
            "sales": "revenue"
        }
        df.rename(columns=rename_map, inplace=True)

        required = ["campaign", "spend", "revenue"]
        if not all(col in df.columns for col in required):
            st.error("CSV must contain campaign, spend, revenue")
            st.stop()

        df["spend"] = pd.to_numeric(df["spend"], errors="coerce")
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
        df.fillna(0, inplace=True)

        df["roas"] = np.where(df["spend"] > 0,
                              df["revenue"] / df["spend"], 0)

        df["profit"] = df["revenue"] - df["spend"]

        df["scale_potential"] = np.where(df["roas"] > 2,
                                         "🔥 High Scale Potential",
                                         np.where(df["roas"] > 1,
                                                  "⚙️ Optimize",
                                                  "❌ Risk"))

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Spend", f"{df['spend'].sum():,.0f}")
        col2.metric("Total Profit", f"{df['profit'].sum():,.0f}")
        col3.metric("Avg ROAS", f"{df['roas'].mean():.2f}")

        fig = px.bar(df, x="campaign", y="profit",
                     color="scale_potential",
                     title="Profit Intelligence")
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df.sort_values("profit", ascending=False),
                     use_container_width=True)

# ====================================================
# 🔮 CAMPAIGN PREDICTOR
# ====================================================

if mode == "🔮 Campaign Predictor":

    st.subheader("Predict Campaign Outcome Before Launch")

    budget = st.number_input("Budget", min_value=0.0)
    expected_ctr = st.slider("Expected CTR %", 0.0, 10.0, 2.0)
    expected_cvr = st.slider("Expected Conversion Rate %", 0.0, 20.0, 5.0)
    avg_order = st.number_input("Average Order Value", min_value=0.0)

    if st.button("Predict Performance"):

        clicks = budget * (expected_ctr / 100) * 10
        conversions = clicks * (expected_cvr / 100)
        revenue = conversions * avg_order

        roas = revenue / budget if budget > 0 else 0

        risk = "Low Risk" if roas > 2 else \
               "Medium Risk" if roas > 1 else \
               "High Risk"

        st.metric("Predicted Revenue", f"{revenue:,.0f}")
        st.metric("Predicted ROAS", f"{roas:.2f}")
        st.metric("Risk Level", risk)

# ====================================================
# 📱 SOCIAL GROWTH ANALYZER
# ====================================================

if mode == "📱 Social Growth Analyzer":

    file = st.file_uploader("Upload Social Insights CSV", type=["csv"])

    if file:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.lower()

        required = ["likes", "comments", "shares", "reach"]
        if not all(col in df.columns for col in required):
            st.error("CSV must contain likes, comments, shares, reach")
            st.stop()

        df.fillna(0, inplace=True)

        df["engagement"] = df["likes"] + df["comments"] + df["shares"]
        df["engagement_rate"] = df["engagement"] / df["reach"]

        avg_eng = df["engagement_rate"].mean()

        if avg_eng > 0.06:
            verdict = "🔥 Viral Page"
        elif avg_eng > 0.04:
            verdict = "🚀 Strong Growth"
        elif avg_eng > 0.02:
            verdict = "⚙ Needs Better Hooks"
        else:
            verdict = "❌ Weak Content Strategy"

        st.metric("Avg Engagement Rate", f"{avg_eng:.2%}")
        st.info(verdict)

        fig = px.line(df, y="engagement_rate",
                      title="Engagement Trend")
        st.plotly_chart(fig, use_container_width=True)
