import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
from fpdf import FPDF
import base64

st.set_page_config(page_title="MTSE Analytics", layout="wide")

# -----------------------
# STYLE
# -----------------------
st.markdown("""
<style>
body {
    background-color: #F5F3EF;
}
.stApp {
    background-color: #F5F3EF;
}
.card {
    background: white;
    padding:20px;
    border-radius:10px;
    box-shadow:0 2px 6px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# USERS
# -----------------------
users = {
    "admin": hashlib.sha256("mtse123".encode()).hexdigest()
}

if "logged" not in st.session_state:
    st.session_state.logged = False

# -----------------------
# LOGIN
# -----------------------
if not st.session_state.logged:
    st.sidebar.title("Login")

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if username in users and users[username] == hashed:
            st.session_state.logged = True
            st.success("Login successful")
        else:
            st.error("Wrong credentials")

# -----------------------
# DASHBOARD
# -----------------------
if st.session_state.logged:

    st.title("MTSE Analytics")
    st.subheader("منصة تحليل البيانات واتخاذ القرار التسويقي")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        required = ["campaign","impressions","clicks","spend","revenue"]
        if not all(col in df.columns for col in required):
            st.error("CSV must contain columns: campaign, impressions, clicks, spend, revenue")
        else:

            df["CTR"] = df["clicks"] / df["impressions"]
            df["CPC"] = df["spend"] / df["clicks"]
            df["ROAS"] = df["revenue"] / df["spend"]

            total_spend = df["spend"].sum()
            total_revenue = df["revenue"].sum()
            avg_roas = df["ROAS"].mean()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Spend", f"{total_spend:,.0f} EGP")
            col2.metric("Total Revenue", f"{total_revenue:,.0f} EGP")
            col3.metric("Average ROAS", f"{avg_roas:.2f}")

            best = df.sort_values("ROAS", ascending=False).iloc[0]
            worst = df.sort_values("ROAS").iloc[0]

            st.success(f"Best Campaign: {best['campaign']}")
            if worst["ROAS"] < 1:
                st.warning(f"Needs Optimization: {worst['campaign']}")

            fig = px.bar(df, x="campaign", y="revenue", title="Revenue by Campaign")
            st.plotly_chart(fig, use_container_width=True)

            # PDF EXPORT
            if st.button("Download PDF Report"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="MTSE Analytics Report", ln=True)
                pdf.cell(200, 10, txt=f"Total Spend: {total_spend}", ln=True)
                pdf.cell(200, 10, txt=f"Total Revenue: {total_revenue}", ln=True)
                pdf.output("report.pdf")
                with open("report.pdf", "rb") as f:
                    st.download_button("Click to Download", f, file_name="report.pdf")

    # -----------------------
    # PRICING
    # -----------------------
    st.markdown("---")
    st.header("Pricing Plans")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Starter")
        st.write("499 جنيه / شهر")
        st.write("تحليل أساسي + رفع CSV")

    with col2:
        st.markdown("### Pro")
        st.write("1499 جنيه / شهر")
        st.write("تحليل ذكي + تقارير + تصدير PDF")

    with col3:
        st.markdown("### Enterprise")
        st.write("حسب الطلب")
        st.write("API + Multi Users + دعم خاص")

    # -----------------------
    # CONTACT
    # -----------------------
    st.markdown("---")
    st.header("Contact")

    st.write("Email: marsatouch@gmail.com")
    st.write("WhatsApp Group:")
    st.write("https://chat.whatsapp.com/BepZmZWVy01EFmU6vrhjo1")
