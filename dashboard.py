import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="MTSE Intelligence", layout="wide")

st.title("📊 MTSE Intelligence")
st.subheader("Smart Campaign Performance Analyzer")

uploaded_file = st.file_uploader("ارفع ملف CSV للحملة", type=["csv"])

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8-sig")

        # تنظيف أسماء الأعمدة
        df.columns = df.columns.str.strip().str.lower()

        # طباعة الأعمدة للتشخيص (مهم جداً)
        st.write("Detected Columns:", list(df.columns))

        # تحويل أسماء الأعمدة إلى صيغة موحدة
        rename_map = {}

        for col in df.columns:
            if "campaign" in col:
                rename_map[col] = "campaign"
            elif "spend" in col or "cost" in col:
                rename_map[col] = "spend"
            elif "revenue" in col or "sales" in col:
                rename_map[col] = "revenue"

        df.rename(columns=rename_map, inplace=True)

        required = {"campaign", "spend", "revenue"}

        if not required.issubset(df.columns):
            st.error("الملف يجب أن يحتوي على أعمدة تمثل الحملة والإنفاق والإيراد")
        else:

            df["spend"] = pd.to_numeric(df["spend"], errors="coerce")
            df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")

            df = df.dropna(subset=["spend", "revenue"])

            df["roas"] = np.where(df["spend"] != 0, df["revenue"] / df["spend"], 0)

            total_spend = df["spend"].sum()
            total_revenue = df["revenue"].sum()
            overall_roas = total_revenue / total_spend if total_spend != 0 else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("إجمالي الإنفاق", f"{total_spend:,.0f}")
            col2.metric("إجمالي الإيراد", f"{total_revenue:,.0f}")
            col3.metric("متوسط ROAS", f"{overall_roas:.2f}")

            st.divider()

            df["performance"] = np.where(
                df["roas"] >= 3, "Strong 🚀",
                np.where(df["roas"] >= 1.5, "Average ⚖️", "Weak 🔻")
            )

            st.dataframe(df)

            fig = px.bar(df, x="campaign", y="revenue",
                         color="performance",
                         title="Revenue by Campaign")
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error("حدث خطأ في قراءة الملف")
        st.write(e)
