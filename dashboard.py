import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
from fpdf import FPDF

st.set_page_config(page_title="MTSE Analytics", layout="wide")

# -------------------- STYLE --------------------

st.markdown("""
<style>
.stApp {
    background-color: #F4F1EA;
}

h1, h2, h3 {
    color: #2E2E2E;
}

.metric-card {
    background: #FFFFFF;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.sidebar .sidebar-content {
    background-color: #ECE8DF;
}
</style>
""", unsafe_allow_html=True)

# -------------------- LOGIN SYSTEM --------------------

users = {
    "admin": hashlib.sha256("mtse123".encode()).hexdigest()
}

if "logged" not in st.session_state:
    st.session_state.logged = False

if not st.session_state.logged:

    st.sidebar.title("تسجيل الدخول")

    username = st.sidebar.text_input("اسم المستخدم")
    password = st.sidebar.text_input("كلمة المرور", type="password")

    if st.sidebar.button("دخول"):
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if username in users and users[username] == hashed:
            st.session_state.logged = True
            st.success("تم تسجيل الدخول")
        else:
            st.error("بيانات غير صحيحة")

# -------------------- MAIN DASHBOARD --------------------

if st.session_state.logged:

    st.title("MTSE Analytics")
    st.subheader("منصة تحليل البيانات واتخاذ القرار التسويقي")

    uploaded_file = st.file_uploader("رفع ملف CSV", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        required = ["campaign","impressions","clicks","spend","revenue"]

        if not all(col in df.columns for col in required):
            st.error("الملف يجب أن يحتوي على الأعمدة: campaign, impressions, clicks, spend, revenue")
        else:

            df["CTR"] = df["clicks"] / df["impressions"]
            df["CPC"] = df["spend"] / df["clicks"]
            df["ROAS"] = df["revenue"] / df["spend"]

            total_spend = df["spend"].sum()
            total_revenue = df["revenue"].sum()
            avg_roas = df["ROAS"].mean()

            col1, col2, col3 = st.columns(3)

            col1.metric("إجمالي الإنفاق", f"{total_spend:,.0f} جنيه")
            col2.metric("إجمالي الإيراد", f"{total_revenue:,.0f} جنيه")
            col3.metric("متوسط ROAS", f"{avg_roas:.2f}")

            best = df.sort_values("ROAS", ascending=False).iloc[0]
            worst = df.sort_values("ROAS").iloc[0]

            st.success(f"أفضل حملة: {best['campaign']}")

            if worst["ROAS"] < 1:
                st.warning(f"تحتاج تحسين: {worst['campaign']}")

            fig = px.bar(df, x="campaign", y="revenue", title="الإيراد حسب الحملة")
            st.plotly_chart(fig, use_container_width=True)

            # PDF
            if st.button("تحميل تقرير PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="MTSE Analytics Report", ln=True)
                pdf.cell(200, 10, txt=f"Total Spend: {total_spend}", ln=True)
                pdf.cell(200, 10, txt=f"Total Revenue: {total_revenue}", ln=True)
                pdf.output("report.pdf")

                with open("report.pdf", "rb") as f:
                    st.download_button("اضغط لتحميل التقرير", f, file_name="report.pdf")

    # ---------------- PRICING ----------------

    st.markdown("---")
    st.header("الباقات")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Starter")
        st.write("499 جنيه / شهر")
        st.write("تحليل أساسي + رفع CSV")

    with col2:
        st.markdown("### Pro")
        st.write("1499 جنيه / شهر")
        st.write("تحليل ذكي + تقارير + PDF")

    with col3:
        st.markdown("### Enterprise")
        st.write("حسب الاتفاق")
        st.write("API + حسابات متعددة + دعم خاص")

    # ---------------- CONTACT ----------------

    st.markdown("---")
    st.header("تواصل معنا")

    st.write("📧 marsatouch@gmail.com")
    st.write("📱 WhatsApp:")
    st.write("https://chat.whatsapp.com/BepZmZWVy01EFmU6vrhjo1")
