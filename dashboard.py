import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import sqlite3
import hashlib
from sklearn.linear_model import LinearRegression
from fpdf import FPDF

# =========================================
# DATABASE SETUP
# =========================================
conn = sqlite3.connect("mtse.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    plan TEXT
)
""")
conn.commit()

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(page_title="MTSE Analytics Pro", layout="wide")

st.markdown("""
<style>
body {background-color:#F4F1EA;}
h1,h2,h3 {color:#2C2C2C;}
.stButton>button {
background-color:#A68A64;
color:white;
border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# AUTH FUNCTIONS
# =========================================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def register_user(u, p, plan):
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)",
                  (u, hash_password(p), plan))
        conn.commit()
        return True
    except:
        return False

def login_user(u, p):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (u, hash_password(p)))
    return c.fetchone()

# =========================================
# AUTH UI
# =========================================
if "logged" not in st.session_state:
    st.session_state.logged = False

menu = st.sidebar.selectbox("الحساب", ["تسجيل دخول", "إنشاء حساب"])

if not st.session_state.logged:

    if menu == "إنشاء حساب":
        st.title("إنشاء حساب جديد")
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        plan = st.selectbox("اختر الباقة", ["Starter", "Pro", "Business"])

        if st.button("تسجيل"):
            if register_user(u, p, plan):
                st.success("تم إنشاء الحساب")
            else:
                st.error("اسم مستخدم موجود")

    if menu == "تسجيل دخول":
        st.title("تسجيل الدخول")
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")

        if st.button("دخول"):
            user = login_user(u, p)
            if user:
                st.session_state.logged = True
                st.session_state.username = user[0]
                st.session_state.plan = user[2]
                st.success("تم تسجيل الدخول")
            else:
                st.error("بيانات غير صحيحة")

    st.stop()

# =========================================
# MAIN APP
# =========================================
st.title("MTSE Analytics Pro")
st.write(f"مرحبًا {st.session_state.username} | الباقة: {st.session_state.plan}")

uploaded = st.file_uploader("ارفع ملف CSV")

if uploaded:
    df = pd.read_csv(uploaded)
    df.columns = df.columns.str.lower().str.strip()

    numeric_cols = df.select_dtypes(include=np.number).columns

    st.subheader("نظرة عامة")
    st.dataframe(df.head())

    col1,col2,col3 = st.columns(3)
    col1.metric("عدد الصفوف", len(df))
    col2.metric("عدد الأعمدة", len(df.columns))
    col3.metric("أعمدة رقمية", len(numeric_cols))

    # =====================================
    # PLAN CONTROL
    # =====================================
    if st.session_state.plan in ["Pro", "Business"]:

        st.subheader("تحليل متقدم")

        if len(numeric_cols) > 0:
            metric = st.selectbox("اختر مؤشر", numeric_cols)

            st.metric("متوسط", round(df[metric].mean(),2))

            fig = px.line(df, y=metric)
            st.plotly_chart(fig, use_container_width=True)

    if st.session_state.plan == "Business":

        st.subheader("التوقعات المستقبلية")

        if len(numeric_cols) > 0:
            target = st.selectbox("اختر عمود للتوقع", numeric_cols)

            df["index"] = range(len(df))
            X = df[["index"]]
            y = df[target]

            model = LinearRegression()
            model.fit(X, y)

            future = np.array(range(len(df)+5)).reshape(-1,1)
            pred = model.predict(future)

            fig = px.line(y=pred, title="Forecast")
            st.plotly_chart(fig)

    # =====================================
    # PDF FOR ALL
    # =====================================
    if st.button("تحميل تقرير PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200,10, txt="MTSE Analytics Report", ln=True)

        for col in numeric_cols:
            pdf.cell(200,10, txt=f"{col} Avg: {round(df[col].mean(),2)}", ln=True)

        pdf.output("report.pdf")

        with open("report.pdf","rb") as f:
            st.download_button("تحميل", f, "MTSE_Report.pdf")

# =========================================
# ADMIN PANEL
# =========================================
if st.session_state.username == "admin":
    st.markdown("---")
    st.subheader("لوحة تحكم المدير")

    c.execute("SELECT username, plan FROM users")
    users_data = c.fetchall()

    admin_df = pd.DataFrame(users_data, columns=["Username","Plan"])
    st.dataframe(admin_df)
