import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import hashlib
import numpy as np
import io
from sklearn.linear_model import LinearRegression
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

st.set_page_config(page_title="MTSE Analytics", layout="wide")

PLATFORM_NAME = "MTSE Analytics"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin@2026"

# -------------------------------------------------
# DATABASE
# -------------------------------------------------

conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT
)
""")
conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# إنشاء الادمن لو مش موجود
c.execute("SELECT * FROM users WHERE username=?", (ADMIN_USERNAME,))
if not c.fetchone():
    c.execute("INSERT INTO users VALUES (?, ?, ?)",
              (ADMIN_USERNAME, hash_password(ADMIN_PASSWORD), "admin"))
    conn.commit()

# -------------------------------------------------
# LANGUAGE
# -------------------------------------------------

language = st.sidebar.selectbox("Language / اللغة", ["English", "العربية"])

def tr(en, ar):
    return en if language == "English" else ar

# -------------------------------------------------
# LOGIN SYSTEM
# -------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user = None

if not st.session_state.logged_in:

    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

        if user and user[1] == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.role = user[2]
            st.session_state.user = username
            st.success("Logged in successfully")
            st.rerun()
        else:
            st.error("Wrong Credentials")

    st.markdown("---")
    st.subheader("Create Account")

    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Create Account"):
        if new_user and new_pass:
            try:
                c.execute("INSERT INTO users VALUES (?, ?, ?)",
                          (new_user, hash_password(new_pass), "user"))
                conn.commit()
                st.success("Account Created")
            except:
                st.error("User already exists")

    st.stop()

# -------------------------------------------------
# MAIN APP
# -------------------------------------------------

st.title(PLATFORM_NAME)
st.write(tr("Data & Marketing Analytics Platform",
            "منصة تحليل البيانات واتخاذ القرار التسويقي"))

st.success(f"Welcome {st.session_state.user}")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)
    st.dataframe(df)

    numeric_cols = df.select_dtypes(include=np.number).columns

    if len(numeric_cols) > 0:

        st.header(tr("Automatic Data Analysis", "تحليل البيانات التلقائي"))

        for col in numeric_cols:
            st.metric(f"{col} Mean", round(df[col].mean(),2))

        fig = px.line(df[numeric_cols])
        st.plotly_chart(fig, use_container_width=True)

        # -------------------------
        # AI TREND PREDICTION
        # -------------------------

        st.header("AI Trend Prediction")

        col_to_predict = st.selectbox("Select Column", numeric_cols)

        X = np.arange(len(df)).reshape(-1,1)
        y = df[col_to_predict].values.reshape(-1,1)

        model = LinearRegression()
        model.fit(X, y)

        future = model.predict([[len(df)]])[0][0]

        st.write("Next Predicted Value:", round(float(future),2))

        # -------------------------
        # AI INSIGHT BOT
        # -------------------------

        st.header("AI Insight Bot")

        if st.button("Generate Insights"):
            insights = []
            for col in numeric_cols:
                mean = df[col].mean()
                insights.append(f"{col} average is {round(mean,2)}")

            for i in insights:
                st.write(i)

        # -------------------------
        # PDF REPORT
        # -------------------------

        def generate_pdf(df, filename):

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph(PLATFORM_NAME + " Report", styles["Heading1"]))
            elements.append(Spacer(1,20))
            elements.append(Paragraph(f"Analyzed File: {filename}", styles["Normal"]))
            elements.append(Spacer(1,20))

            for col in numeric_cols:
                elements.append(
                    Paragraph(f"{col} Mean: {round(df[col].mean(),2)}",
                              styles["Normal"])
                )
                elements.append(Spacer(1,10))

            elements.append(Spacer(1,40))
            elements.append(
                Paragraph("Generated by MTSE Analytics Platform",
                          styles["Normal"])
            )

            doc.build(elements)
            buffer.seek(0)
            return buffer

        if st.button("Generate Enterprise Report"):
            pdf_buffer = generate_pdf(df, uploaded_file.name)

            st.download_button(
                "Download PDF Report",
                data=pdf_buffer,
                file_name="MTSE_Report.pdf",
                mime="application/pdf"
            )

# -------------------------------------------------
# ADMIN PANEL
# -------------------------------------------------

if st.session_state.role == "admin":
    st.markdown("---")
    st.header("Admin Panel")

    users_df = pd.read_sql("SELECT username, role FROM users", conn)
    st.dataframe(users_df)
