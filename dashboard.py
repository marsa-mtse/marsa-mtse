import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import hashlib
import numpy as np
import io
from datetime import datetime
from sklearn.linear_model import LinearRegression
from fpdf import FPDF

# ================= CONFIG =================
st.set_page_config(page_title="MTSE Analytics", layout="wide")

# ================= DATABASE =================
conn = sqlite3.connect("mtse_users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
username TEXT PRIMARY KEY,
password TEXT,
role TEXT
)
""")

conn.commit()

# Default Admin
admin_user = "admin"
admin_pass = hashlib.sha256("admin@2026".encode()).hexdigest()

c.execute("SELECT * FROM users WHERE username=?", (admin_user,))
if not c.fetchone():
    c.execute("INSERT INTO users VALUES (?,?,?)",
              (admin_user, admin_pass, "admin"))
    conn.commit()

# ================= LANGUAGE =================
lang = st.sidebar.selectbox("Language / اللغة", ["English", "العربية"])

def t(en, ar):
    return en if lang == "English" else ar

# ================= WATERMARK =================
st.markdown("""
<style>
.watermark {
position: fixed;
top: 40%;
left: 30%;
opacity: 0.05;
font-size: 80px;
transform: rotate(-30deg);
z-index: -1;
}
</style>
<div class="watermark">MTSE Analytics</div>
""", unsafe_allow_html=True)

# ================= LOGIN =================
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

if not st.session_state.user:

    st.title("📊 MTSE Analytics")
    st.subheader(t("Data & Marketing Analytics Platform",
                   "منصة تحليل البيانات واتخاذ القرار"))

    menu = st.radio("", [t("Login", "تسجيل الدخول"),
                         t("Create Account", "إنشاء حساب")])

    if menu == t("Login", "تسجيل الدخول"):
        u = st.text_input(t("Username", "اسم المستخدم"))
        p = st.text_input(t("Password", "كلمة المرور"), type="password")

        if st.button(t("Login", "دخول")):
            c.execute("SELECT * FROM users WHERE username=? AND password=?",
                      (u, hash_pass(p)))
            result = c.fetchone()
            if result:
                st.session_state.user = u
                st.session_state.role = result[2]
                st.rerun()
            else:
                st.error(t("Wrong Credentials", "بيانات غير صحيحة"))

    else:
        new_u = st.text_input(t("New Username", "اسم مستخدم جديد"))
        new_p = st.text_input(t("New Password", "كلمة مرور جديدة"),
                              type="password")

        if st.button(t("Create", "إنشاء")):
            try:
                c.execute("INSERT INTO users VALUES (?,?,?)",
                          (new_u, hash_pass(new_p), "user"))
                conn.commit()
                st.success(t("Account Created", "تم إنشاء الحساب"))
            except:
                st.error(t("Username Exists", "اسم المستخدم موجود"))

# ================= DASHBOARD =================
else:

    st.success(t("Welcome", "مرحباً") + f" {st.session_state.user}")

    uploaded = st.file_uploader(
        t("Upload CSV File", "ارفع ملف CSV"),
        type=["csv"]
    )

    if uploaded:

        df = pd.read_csv(uploaded)
        st.dataframe(df.head())

        numeric_cols = df.select_dtypes(include=np.number).columns

        # ================= AUTO ANALYSIS =================
        st.header(t("Automatic Data Analysis",
                    "تحليل البيانات التلقائي"))

        for col in numeric_cols:
            fig = px.line(df, y=col, title=col)
            st.plotly_chart(fig, use_container_width=True)

        # ================= AI Prediction =================
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            X = np.arange(len(df)).reshape(-1, 1)
            y = df[col].values

            model = LinearRegression()
            model.fit(X, y)

            future = model.predict([[len(df)]])[0]

            st.subheader(t("AI Prediction",
                           "توقعات الذكاء الاصطناعي"))

            st.write(
                t("Next Predicted Value:",
                  "القيمة المتوقعة القادمة:"),
                round(float(future), 2)
            )

        # ================= BOT INSIGHT =================
        st.subheader("AI Insight Bot 🤖")

        if st.button(t("Generate Insights",
                       "توليد استنتاجات ذكية")):

            summary = df.describe().to_string()
            st.text(summary)

        # ================= PROFESSIONAL PDF =================
        if st.button(t("Generate Enterprise Report",
                       "إنشاء تقرير احترافي")):

            pdf = FPDF()
            pdf.add_page()

            pdf.set_font("Arial", "B", 20)
            pdf.cell(200, 15, "MTSE Analytics Report", ln=True, align="C")

            pdf.set_font("Arial", "", 12)
            pdf.cell(200, 8,
                     f"User: {st.session_state.user}",
                     ln=True)
            pdf.cell(200, 8,
                     f"File: {uploaded.name}",
                     ln=True)
            pdf.cell(200, 8,
                     f"Date: {datetime.now().strftime('%Y-%m-%d')}",
                     ln=True)

            pdf.ln(10)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Data Summary", ln=True)

            pdf.set_font("Arial", "", 12)
            for col in numeric_cols:
                pdf.cell(
                    200, 8,
                    f"{col} Avg: {round(df[col].mean(),2)}",
                    ln=True
                )

            pdf.ln(10)
            pdf.cell(
                200, 10,
                "Generated by MTSE Analytics Platform",
                ln=True, align="C"
            )

            buffer = io.BytesIO()
            pdf.output(buffer)
            buffer.seek(0)

            st.download_button(
                label=t("Download Report",
                        "تحميل التقرير"),
                data=buffer,
                file_name="MTSE_Enterprise_Report.pdf",
                mime="application/pdf"
            )

    # ================= ADMIN PANEL =================
    if st.session_state.role == "admin":
        st.header(t("Admin Panel",
                    "لوحة تحكم المدير"))

        users = pd.read_sql_query("SELECT username, role FROM users", conn)
        st.dataframe(users)

    if st.button(t("Logout", "تسجيل خروج")):
        st.session_state.user = None
        st.rerun()
