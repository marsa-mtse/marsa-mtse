import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MTSE Intelligence", layout="wide")

st.title("📊 MTSE لوحة تحكم حملة")

uploaded_file = st.file_uploader("ارفع ملف الحملة CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    total_spend = df["spend"].sum()
    total_revenue = df["revenue"].sum()
    roas = total_revenue / total_spend if total_spend != 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي الإنفاق", f"{total_spend:.2f}")
    col2.metric("إجمالي الإيراد", f"{total_revenue:.2f}")
    col3.metric("متوسط ROAS", f"{roas:.2f}")

    fig = px.bar(df, x="campaign", y="revenue", title="Revenue by Campaign")
    st.plotly_chart(fig, use_container_width=True)
