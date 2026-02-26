import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MTSE Intelligence", layout="wide")

st.title("📊 MTSE Intelligence Dashboard")

uploaded_file = st.file_uploader("ارفع ملف CSV للحملة", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # تنظيف أسماء الأعمدة
    df.columns = df.columns.str.strip().str.lower()

    required_columns = {"campaign", "spend", "revenue"}

    if not required_columns.issubset(df.columns):
        st.error("الملف لازم يحتوي على الأعمدة: campaign, spend, revenue")
    else:
        # تحويل القيم لأرقام
        df["spend"] = pd.to_numeric(df["spend"], errors="coerce")
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")

        df = df.dropna(subset=["spend", "revenue"])

        total_spend = df["spend"].sum()
        total_revenue = df["revenue"].sum()
        roas = total_revenue / total_spend if total_spend != 0 else 0

        col1, col2, col3 = st.columns(3)

        col1.metric("إجمالي الإنفاق", f"{total_spend:,.0f}")
        col2.metric("إجمالي الإيراد", f"{total_revenue:,.0f}")
        col3.metric("متوسط ROAS", f"{roas:.2f}")

        fig = px.bar(df, x="campaign", y="revenue", title="Revenue by Campaign")
        st.plotly_chart(fig, use_container_width=True)
