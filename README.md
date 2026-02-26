import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import sqlite3
import hashlib
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="MTSE Analytics", layout="wide")

# =========================
# SOFT UI DESIGN
# =========================
st.markdown("""
<style>
.stApp {
    background-color:#f4f4f5;
    color:#1f2937;
}
h1,h2,h3,h4 {
    color:#1f2937 !important;
}
section[data-testid="stSidebar"] {
    background-color:#e7e5e4;
}
.stMetric {
    background:#ffffff;
    padding:15px;
    border-radius:12px;
    border:1px solid #e5e7eb;
}
.card {
    background:#ffffff;
    padding:25px;
    border-radius:15px;
    border:1px solid #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    try:
        c.execute("INSERT INTO users VALUES (?,?)",
                  (username, hash_password(password)))
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    return c.fetchone()

# =========================
# AUTH
# =========================
if "auth" not in st.session_state:
    st.session_state.auth = False

menu = st.sidebar.selectbox("الحساب", ["تسجيل دخول","إنشاء حساب"])

if not st.session_state.auth:

    if menu == "إنشاء حساب":
        st.title("إنشاء حساب")
        new_user = st.text_input("اسم المستخدم")
        new_pass = st.text_input("كلمة المرور", type="password")

        if st.button("إنشاء"):
            if add_user(new_user,new_pass):
                st.success("تم إنشاء الحساب")
            else:
                st.error("اسم المستخدم موجود")

    if menu == "تسجيل دخول":
        st.title("تسجيل الدخول")
        user = st.text_input("اسم المستخدم")
        pwd = st.text_input("كلمة المرور", type="password")

        if st.button("دخول"):
            if login_user(user,pwd):
                st.session_state.auth=True
                st.success("تم تسجيل الدخول")
            else:
                st.error("بيانات غير صحيحة")

if not st.session_state.auth:
    st.stop()

# =========================
# HEADER
# =========================
st.title("MTSE Analytics")
st.subheader("منصة تحليل البيانات واتخاذ القرار التسويقي")

# =========================
# FILE UPLOAD
# =========================
uploaded = st.file_uploader("ارفع ملف CSV للحملة", type=["csv"])

if uploaded:

    df = pd.read_csv(uploaded)
    df.columns = df.columns.str.lower().str.strip()

    alias_map = {
        "ad_name":"campaign",
        "campaign_name":"campaign"
    }
    df.rename(columns=alias_map, inplace=True)

    required = ["campaign","impressions","clicks","spend","revenue"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        st.error(f"الأعمدة الناقصة: {missing}")
        st.stop()

    df.fillna(0,inplace=True)

    df["ctr"] = np.where(df["impressions"]>0,
                         df["clicks"]/df["impressions"],0)
    df["cpc"] = np.where(df["clicks"]>0,
                         df["spend"]/df["clicks"],0)
    df["roas"] = np.where(df["spend"]>0,
                          df["revenue"]/df["spend"],0)

    total_spend = df["spend"].sum()
    total_revenue = df["revenue"].sum()
    overall_roas = total_revenue/total_spend if total_spend>0 else 0

    best = df.sort_values("roas",ascending=False).iloc[0]["campaign"]
    worst = df.sort_values("roas").iloc[0]["campaign"]

    col1,col2,col3 = st.columns(3)
    col1.metric("إجمالي الإنفاق", f"{total_spend:,.0f} جنيه")
    col2.metric("إجمالي الإيراد", f"{total_revenue:,.0f} جنيه")
    col3.metric("متوسط ROAS", f"{overall_roas:.2f}")

    st.success(f"🏆 أفضل حملة: {best}")
    st.warning(f"⚠ تحتاج تحسين: {worst}")

    st.markdown("## 🤖 توصيات ذكية")

    if overall_roas < 1:
        st.error("الحملة خاسرة – يجب تحسين الاستهداف والإبداع.")
    elif overall_roas < 2:
        st.info("الحملة مربحة لكن يمكن زيادتها تدريجياً.")
    else:
        st.success("أداء قوي – يمكن زيادة الميزانية بثقة.")

    fig = px.bar(df,x="campaign",y="revenue",
                 color="roas")
    st.plotly_chart(fig,use_container_width=True)

    # PDF
    if st.button("تحميل تقرير PDF"):
        doc = SimpleDocTemplate("report.pdf")
        styles = getSampleStyleSheet()
        elements=[]
        elements.append(Paragraph("MTSE Analytics Report", styles["Title"]))
        elements.append(Spacer(1,0.5*inch))
        elements.append(Paragraph(f"Total Spend: {total_spend}", styles["Normal"]))
        elements.append(Paragraph(f"Total Revenue: {total_revenue}", styles["Normal"]))
        elements.append(Paragraph(f"ROAS: {overall_roas:.2f}", styles["Normal"]))
        doc.build(elements)
        with open("report.pdf","rb") as f:
            st.download_button("تحميل الملف",f,file_name="MTSE_Report.pdf")

# =========================
# PRICING
# =========================
st.markdown("---")
st.header("الباقات")

col1,col2,col3 = st.columns(3)

with col1:
    st.markdown("<div class='card'><h3>Starter</h3><h2>499 جنيه</h2><p>تحليل أساسي</p></div>",unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'><h3>Pro</h3><h2>1,299 جنيه</h2><p>تحليل متقدم + PDF</p></div>",unsafe_allow_html=True)

with col3:
    st.markdown("<div class='card'><h3>Business</h3><h2>2,999 جنيه</h2><p>حسابات متعددة + دعم</p></div>",unsafe_allow_html=True)

# =========================
# CONTACT
# =========================
st.markdown("---")
st.header("تواصل معنا")
st.markdown("""
<div class='card'>
📧 marsatouch@gmail.com <br><br>
📱 https://chat.whatsapp.com/BepZmZWVy01EFmU6vrhjo1
</div>
""",unsafe_allow_html=True)

# =========================
# CHAT BOT
# =========================
st.markdown("---")
st.header("مساعد MTSE")

question = st.text_input("اسأل عن تحليل حملتك")

if question:
    if "roas" in question.lower():
        st.write("ROAS هو العائد مقابل الإنفاق الإعلاني.")
    elif "أفضل" in question:
        st.write(f"أفضل حملة هي: {best}")
    else:
        st.write("يمكنني مساعدتك في تحسين الأداء وتحليل النتائج.")
