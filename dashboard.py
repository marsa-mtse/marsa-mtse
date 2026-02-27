# ==============================
# MTSE Analytics - Official Stable v1.0
# ==============================

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import hashlib
import plotly.express as px
from sklearn.linear_model import LinearRegression
import pdfplumber
import docx
import qrcode
from PIL import Image
import io
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics

# ==============================
# CONFIG
# ==============================

st.set_page_config(page_title="MTSE Analytics", layout="wide")
PLATFORM_NAME = "MTSE Analytics"

# ==============================
# STYLE
# ==============================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #1f2937, #111827);
    color: white;
}
h1, h2, h3 {
    color: #facc15;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# DATABASE
# ==============================

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

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# Admin
admin_user = "admin"
admin_pass = hash_password("admin@2026")

c.execute("SELECT * FROM users WHERE username=?", (admin_user,))
if not c.fetchone():
    c.execute("INSERT INTO users VALUES (?,?,?)",
              (admin_user, admin_pass, "admin"))
    conn.commit()

# ==============================
# AUTH
# ==============================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None

if not st.session_state.logged_in:

    st.title("MTSE Analytics")

    option = st.radio("", ["Login", "Create Account"])

    if option == "Login":
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            c.execute("SELECT * FROM users WHERE username=?", (u,))
            user = c.fetchone()
            if user and user[1] == hash_password(p):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.session_state.role = user[2]
                st.rerun()
            else:
                st.error("Wrong Credentials")

    else:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")

        if st.button("Create"):
            try:
                c.execute("INSERT INTO users VALUES (?,?,?)",
                          (new_u, hash_password(new_p), "user"))
                conn.commit()
                st.success("Account Created")
            except:
                st.error("User Exists")

    st.stop()

# ==============================
# MAIN DASHBOARD
# ==============================

st.title(PLATFORM_NAME)
st.success(f"Welcome {st.session_state.user}")

uploaded_file = st.file_uploader(
    "Upload File",
    type=["csv", "xlsx", "pdf", "docx", "txt"]
)

df = None
text_content = ""

if uploaded_file:

    ext = uploaded_file.name.split(".")[-1].lower()

    if ext == "csv":
        df = pd.read_csv(uploaded_file)

    elif ext == "xlsx":
        df = pd.read_excel(uploaded_file)

    elif ext == "pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text_content += page.extract_text() or ""

    elif ext == "docx":
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text_content += para.text + "\n"

    elif ext == "txt":
        text_content = uploaded_file.read().decode("utf-8")

# ==============================
# NUMERIC ANALYSIS
# ==============================

if df is not None:

    st.dataframe(df)

    numeric_cols = df.select_dtypes(include=np.number).columns

    if len(numeric_cols) > 0:

        st.header("Numeric Analysis")

        for col in numeric_cols:
            st.metric(f"{col} Mean", round(df[col].mean(),2))

        fig = px.line(df[numeric_cols])
        st.plotly_chart(fig)

        st.subheader("AI Prediction")
        col_choice = st.selectbox("Select Column", numeric_cols)

        X = np.arange(len(df)).reshape(-1,1)
        y = df[col_choice].values.reshape(-1,1)

        model = LinearRegression()
        model.fit(X, y)
        future = model.predict([[len(df)]])[0][0]

        st.write("Next Predicted Value:", round(float(future),2))

# ==============================
# TEXT ANALYSIS
# ==============================

if text_content:
    st.header("Text Analysis")

    word_count = len(text_content.split())
    char_count = len(text_content)

    st.write("Word Count:", word_count)
    st.write("Character Count:", char_count)

# ==============================
# ENTERPRISE PDF
# ==============================

def generate_enterprise_pdf(df=None, text_data=None, username="User", filename="File"):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

    elements.append(Paragraph("MTSE Analytics", styles["Heading1"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Enterprise Report | تقرير احترافي", styles["Heading2"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Client / المستخدم: {username}", styles["Normal"]))
    elements.append(Paragraph(f"File / الملف: {filename}", styles["Normal"]))
    elements.append(PageBreak())

    if df is not None:
        numeric_cols = df.select_dtypes(include=np.number).columns
        if len(numeric_cols) > 0:
            table_data = [["Metric", "Average"]]
            for col in numeric_cols:
                table_data.append([col, str(round(df[col].mean(),2))])

            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.darkblue),
                ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                ('GRID',(0,0),(-1,-1),0.5,colors.grey),
            ]))
            elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

if uploaded_file:
    st.markdown("---")
    if st.button("Generate Enterprise PDF Report"):
        pdf_buffer = generate_enterprise_pdf(
            df=df,
            text_data=text_content,
            username=st.session_state.user,
            filename=uploaded_file.name
        )
        st.download_button(
            "Download Enterprise Report",
            data=pdf_buffer,
            file_name="MTSE_Enterprise_Report.pdf",
            mime="application/pdf"
        )

# ==============================
# ADMIN PANEL
# ==============================

if st.session_state.role == "admin":
    st.header("Admin Panel")
    users = pd.read_sql("SELECT username, role FROM users", conn)
    st.dataframe(users)
