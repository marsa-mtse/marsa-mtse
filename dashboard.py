import streamlit as st
import pandas as pd

st.set_page_config(page_title="MTSE Data System", layout="wide")

st.title("📊 MTSE Campaign Dashboard")

df = pd.read_csv("campaign_data.csv")

df["CTR"] = df["Clicks"] / df["Impressions"]
df["CPC"] = df["Spend"] / df["Clicks"]
df["ROAS"] = df["Revenue"] / df["Spend"]

total_spend = df["Spend"].sum()
total_revenue = df["Revenue"].sum()
avg_roas = df["ROAS"].mean()

col1, col2, col3 = st.columns(3)

col1.metric("Total Spend", f"{total_spend}")
col2.metric("Total Revenue", f"{total_revenue}")
col3.metric("Average ROAS", round(avg_roas,2))

st.subheader("ROAS Comparison")
st.bar_chart(df.set_index("Ad_Name")["ROAS"])

best_ad = df.sort_values(by="ROAS", ascending=False).iloc[0]

st.success(f"Best Performing Ad: {best_ad['Ad_Name']}")