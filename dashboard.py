if uploaded:

    df = pd.read_csv(uploaded)

    # Clean columns
    df.columns = df.columns.str.lower().str.strip()

    # Column flexibility mapping
    rename_map = {
        "ad_name": "campaign",
        "campaign_name": "campaign"
    }

    df.rename(columns=rename_map, inplace=True)

    required = ["campaign","impressions","clicks","spend","revenue"]

    missing = [c for c in required if c not in df.columns]

    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

    # Prevent division by zero
    df["ctr"] = np.where(df["impressions"]>0, df["clicks"]/df["impressions"], 0)
    df["cpc"] = np.where(df["clicks"]>0, df["spend"]/df["clicks"], 0)
    df["roas"] = np.where(df["spend"]>0, df["revenue"]/df["spend"], 0)
    df["engagement_rate"] = np.where(df["impressions"]>0, df["clicks"]/df["impressions"],0)

    # ===============================
    # TOTAL METRICS
    # ===============================
    total_spend = df["spend"].sum()
    total_revenue = df["revenue"].sum()
    overall_roas = total_revenue / total_spend if total_spend>0 else 0
    avg_ctr = df["ctr"].mean()
    avg_cpc = df["cpc"].mean()
    avg_engagement = df["engagement_rate"].mean()

    best = df.sort_values("roas",ascending=False).iloc[0]["campaign"]
    worst = df.sort_values("roas").iloc[0]["campaign"]

    # ===============================
    # DASHBOARD METRICS
    # ===============================
    col1,col2,col3,col4,col5,col6 = st.columns(6)

    col1.metric("Spend", f"${total_spend:,.0f}")
    col2.metric("Revenue", f"${total_revenue:,.0f}")
    col3.metric("ROAS", f"{overall_roas:.2f}")
    col4.metric("CTR", f"{avg_ctr:.2%}")
    col5.metric("CPC", f"${avg_cpc:.2f}")
    col6.metric("Engagement", f"{avg_engagement:.2%}")

    st.success(f"🏆 Best Campaign: {best}")
    st.error(f"⚠ Needs Optimization: {worst}")

    # ===============================
    # AI RECOMMENDATION ENGINE
    # ===============================
    st.markdown("## 🤖 Smart Insights")

    if overall_roas < 1:
        st.warning("Campaign is losing money. Optimize targeting & creatives.")
    elif overall_roas < 2:
        st.info("Campaign is profitable but can scale with better creatives.")
    else:
        st.success("Strong performance. Consider scaling budget.")

    # ===============================
    # VISUALS
    # ===============================
    fig1 = px.bar(df, x="campaign", y="revenue",
                  color="roas",
                  title="Revenue & ROAS by Campaign")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(df, x="spend", y="revenue",
                      size="clicks",
                      color="roas",
                      title="Spend vs Revenue")
    st.plotly_chart(fig2, use_container_width=True)

# ===============================
# PRICING SECTION
# ===============================
st.markdown("---")
st.header("💰 Pricing Plans")

col1,col2,col3 = st.columns(3)

col1.markdown("### Starter\n$49/month\n✔ Basic Analytics\n✔ CSV Upload")
col2.markdown("### Pro\n$149/month\n✔ AI Insights\n✔ Social Analysis\n✔ Exports")
col3.markdown("### Enterprise\nCustom\n✔ API\n✔ Multi Users\n✔ Dedicated Support")

# ===============================
# CONTACT
# ===============================
st.markdown("---")
st.header("📞 Contact")

st.write("📧 marsatouch@gmail.com")
st.write("📱 WhatsApp Group:")
st.write("https://chat.whatsapp.com/BepZmZWVy01EFmU6vrhjo1?mode=hqctcla")
