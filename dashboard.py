from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.units import inch
from datetime import datetime
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

# ==============================
# CONFIG
# ==============================

st.set_page_config(page_title="MTSE Analytics", layout="wide")
PLATFORM_NAME = "MTSE Analytics"

# ==============================
# STYLE (Professional Theme)
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
.sidebar .sidebar-content {
    background-color: #0f172a;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# WATERMARK
# ==============================

st.markdown("""
<style>
body::before {
content: "MTSE Analytics";
position: fixed;
top: 40%;
left: 25%;
font-size: 90px;
color: rgba(255,255,255,0.05);
transform: rotate(-30deg);
z-index: 0;
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

# Admin Default
admin_user = "admin"
admin_pass = hash_password("admin@2026")

c.execute("SELECT * FROM users WHERE username=?", (admin_user,))
if not c.fetchone():
    c.execute("INSERT INTO users VALUES (?,?,?)",
              (admin_user, admin_pass, "admin"))
    conn.commit()

# ==============================
# LANGUAGE
# ==============================

language = st.sidebar.selectbox("Language / اللغة", ["English", "العربية"])

def tr(en, ar):
    return en if language == "English" else ar

# ==============================
# QR CODES
# ==============================

def generate_qr(data):
    qr = qrcode.make(data)
    buffer = io.BytesIO()
    qr.save(buffer)
    buffer.seek(0)
    return buffer

st.sidebar.markdown("## Contact")

whatsapp_qr = generate_qr("https://chat.whatsapp.com/BepZmZWVy01EFmU6vrhjo1")
email_qr = generate_qr("mailto:marsatouch@gmail.com")

st.sidebar.image(whatsapp_qr, caption="WhatsApp")
st.sidebar.image(email_qr, caption="Email")

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
    tr("Upload File", "ارفع ملف"),
    type=["csv", "xlsx", "pdf", "docx", "txt"]
)

text_content = ""

if uploaded_file:

    file_type = uploaded_file.name.split(".")[-1]

    # CSV
    if file_type == "csv":
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)

    # Excel
    elif file_type == "xlsx":
        df = pd.read_excel(uploaded_file)
        st.dataframe(df)

    # PDF
    elif file_type == "pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text_content += page.extract_text() + "\n"
        st.text_area("Extracted Text", text_content)

    # Word
    elif file_type == "docx":
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text_content += para.text + "\n"
        st.text_area("Extracted Text", text_content)

    # TXT
    elif file_type == "txt":
        text_content = uploaded_file.read().decode("utf-8")
        st.text_area("Text Content", text_content)

    # =======================
    # NUMERIC ANALYSIS
    # =======================

    if 'df' in locals():
        numeric_cols = df.select_dtypes(include=np.number).columns

        if len(numeric_cols) > 0:
            st.header("Automatic Numeric Analysis")

            for col in numeric_cols:
                st.metric(col + " Mean", round(df[col].mean(),2))

            fig = px.line(df[numeric_cols])
            st.plotly_chart(fig)

            # AI Prediction
            st.subheader("AI Trend Prediction")
            col_choice = st.selectbox("Select Column", numeric_cols)

            X = np.arange(len(df)).reshape(-1,1)
            y = df[col_choice].values.reshape(-1,1)

            model = LinearRegression()
            model.fit(X, y)
            future = model.predict([[len(df)]])[0][0]

            st.write("Next Predicted Value:", round(float(future),2))

    # =======================
    # TEXT ANALYSIS
    # =======================

    if text_content:
        st.header("Text Analysis")

        word_count = len(text_content.split())
        char_count = len(text_content)

        st.write("Word Count:", word_count)
        st.write("Character Count:", char_count)

        if st.button("AI Text Insight"):
            st.write("Most Common Words (Basic):")
            words = text_content.lower().split()
            common = pd.Series(words).value_counts().head(10)
            st.write(common)

# ==============================
# AI CHATBOT
# ==============================

st.header("AI Insight Bot")

user_question = st.text_input("Ask anything about your uploaded data")

if user_question:
    st.write("AI Response:")
    st.write("Based on current data, deeper insights require GPT integration in next version.")

# ==============================
# ADMIN PANEL
# ==============================

if st.session_state.role == "admin":
    st.header("Admin Panel")
    users = pd.read_sql("SELECT username, role FROM users", conn)
    st.dataframe(users)
    # ==============================
# ENTERPRISE PDF REPORT ENGINE
# ==============================

def generate_enterprise_pdf(df=None, text_data=None, username="User", filename="File"):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    # ---------- COVER PAGE ----------
    elements.append(Paragraph("MTSE Analytics", title_style))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Enterprise Data Intelligence Report", styles["Heading2"]))
    elements.append(Spacer(1, 30))

    elements.append(Paragraph(f"Client / المستخدم: {username}", normal_style))
    elements.append(Paragraph(f"File / الملف: {filename}", normal_style))
    elements.append(Paragraph(f"Date / التاريخ: {datetime.now().strftime('%Y-%m-%d')}", normal_style))

    elements.append(PageBreak())

    # ---------- EXECUTIVE SUMMARY ----------
    elements.append(Paragraph("Executive Summary | الملخص التنفيذي", styles["Heading2"]))
    elements.append(Spacer(1, 15))

    summary_text = """
    This report provides automated AI-driven insights based on uploaded data.
    يقدم هذا التقرير تحليلاً ذكياً تلقائياً بناءً على البيانات المرفوعة.
    """

    elements.append(Paragraph(summary_text, normal_style))
    elements.append(Spacer(1, 20))

    # ---------- NUMERIC DATA ----------
    if df is not None:
        numeric_cols = df.select_dtypes(include=np.number).columns

        if len(numeric_cols) > 0:

            elements.append(Paragraph("Data Metrics | مؤشرات البيانات", styles["Heading2"]))
            elements.append(Spacer(1, 15))

            table_data = [["Metric / المؤشر", "Average / المتوسط"]]

            for col in numeric_cols:
                table_data.append([col, str(round(df[col].mean(),2))])

            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#1f2937")),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
                ('FONTSIZE',(0,0),(-1,-1),10),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 20))

    # ---------- TEXT ANALYSIS ----------
    if text_data:
        elements.append(Paragraph("Text Analysis | تحليل النصوص", styles["Heading2"]))
        elements.append(Spacer(1, 15))

        word_count = len(text_data.split())
        char_count = len(text_data)

        elements.append(Paragraph(f"Word Count / عدد الكلمات: {word_count}", normal_style))
        elements.append(Paragraph(f"Character Count / عدد الحروف: {char_count}", normal_style))

        elements.append(Spacer(1, 20))

    # ---------- FOOTER & WATERMARK ----------
    def add_watermark(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 60)
        canvas.setFillGray(0.92)
        canvas.drawCentredString(A4[0]/2, A4[1]/2, "MTSE Analytics")
        canvas.restoreState()

        canvas.setFont("Helvetica", 9)
        canvas.drawString(30, 20, "Generated by MTSE Analytics Platform")
        canvas.drawRightString(A4[0]-30, 20, "Confidential")

    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)

    buffer.seek(0)
    return buffer
    st.markdown("---")
st.subheader("Enterprise Report")

if st.button("Generate Enterprise PDF Report"):

    pdf_buffer = generate_enterprise_pdf(
        df=df if 'df' in locals() else None,
        text_data=text_content if text_content else None,
        username=st.session_state.user,
        filename=uploaded_file.name
    )

    st.download_button(
        "Download Enterprise Report",
        data=pdf_buffer,
        file_name="MTSE_Enterprise_Report.pdf",
        mime="application/pdf"
    )
    
