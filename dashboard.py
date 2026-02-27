# ==========================================================
# MTSE Marketing Engine - SaaS Edition v1.0 (PART 1)
# Core Architecture + Auth + Plans + Usage + Admin
# ==========================================================

import streamlit as st
import sqlite3
import hashlib
import datetime
import io
import arabic_reshaper
from bidi.algorithm import get_display
# ==============================
# CONFIG
# ==============================

st.set_page_config(page_title="MTSE Marketing Engine", layout="wide")

PLATFORM_NAME = "MTSE Marketing Engine"
ADMIN_DEFAULT_PASSWORD = "admin@2026"

# ==============================
# PREMIUM STYLE
# ==============================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #0f172a, #1e293b);
    color: white;
}
h1, h2, h3 {
    color: #facc15;
}
.logo-container {
    display: flex;
    align-items: center;
    gap: 12px;
}
.watermark {
    position: fixed;
    top: 40%;
    left: 25%;
    font-size: 80px;
    color: rgba(255,255,255,0.04);
    transform: rotate(-30deg);
    z-index: -1;
}
</style>
<div class="watermark">MTSE Marketing Engine</div>
""", unsafe_allow_html=True)

# ==============================
# LOGO HEADER
# ==============================

st.markdown("""
<div class="logo-container">
    <h1>📊 MTSE Marketing Engine</h1>
</div>
""", unsafe_allow_html=True)

# ==============================
# DATABASE INIT
# ==============================

conn = sqlite3.connect("mtse_saas.db", check_same_thread=False)
c = conn.cursor()

# Users table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT,
    plan TEXT,
    reports_used INTEGER DEFAULT 0,
    uploads_used INTEGER DEFAULT 0,
    created_at TEXT
)
""")

# Reports archive
c.execute("""
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    file_name TEXT,
    created_at TEXT,
    summary TEXT,
    pdf_data BLOB
)
""")

# Activity log
c.execute("""
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    action TEXT,
    timestamp TEXT
)
""")

conn.commit()

# ==============================
# PASSWORD HASH
# ==============================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==============================
# CREATE DEFAULT ADMIN
# ==============================

c.execute("SELECT * FROM users WHERE username='admin'")
if not c.fetchone():
    c.execute("""
    INSERT INTO users 
    (username, password, role, plan, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
        "admin",
        hash_password(ADMIN_DEFAULT_PASSWORD),
        "admin",
        "Business",
        datetime.datetime.now().isoformat()
    ))
    conn.commit()

# ==============================
# SESSION INIT
# ==============================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.plan = None

# ==============================
# PLAN LIMITS
# ==============================

PLAN_LIMITS = {
    "Starter": {"reports": 5, "uploads": 5},
    "Pro": {"reports": 25, "uploads": 25},
    "Business": {"reports": 9999, "uploads": 9999}
}

# ==============================
# LOGIN / REGISTER
# ==============================

if not st.session_state.logged_in:

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

        if user and user[1] == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.username = user[0]
            st.session_state.role = user[2]
            st.session_state.plan = user[3]
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials")

    st.stop()

# ==========================================================
# USER DASHBOARD (After Login)
# ==========================================================

st.success(f"Welcome {st.session_state.username}")
st.write(f"Role: {st.session_state.role}")
st.write(f"Plan: {st.session_state.plan}")

# ==============================
# USAGE DISPLAY
# ==============================

c.execute("SELECT reports_used, uploads_used FROM users WHERE username=?", 
          (st.session_state.username,))
usage = c.fetchone()

reports_used = usage[0]
uploads_used = usage[1]

limits = PLAN_LIMITS[st.session_state.plan]

st.markdown("---")
st.subheader("Usage")

col1, col2 = st.columns(2)
col1.metric("Reports Used", f"{reports_used} / {limits['reports']}")
col2.metric("Uploads Used", f"{uploads_used} / {limits['uploads']}")

# ==============================
# ADMIN PANEL
# ==============================

if st.session_state.role == "admin":

    st.markdown("---")
    st.header("Admin Panel")

    st.subheader("All Users")

    users_df = c.execute("SELECT username, role, plan FROM users").fetchall()

    for u in users_df:
        st.write(u)

    st.subheader("Create User")

    new_user = st.text_input("New Username")
    new_password = st.text_input(
    "New Password",
    type="password",
    key="admin_change_password_input"
)    
    new_plan = st.selectbox("Plan", ["Starter", "Pro", "Business"])
    new_role = st.selectbox("Role", ["Analyst", "Viewer", "Marketing Manager"])

    if st.button("Create User"):
        try:
            c.execute("""
            INSERT INTO users 
            (username, password, role, plan, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (
                new_user,
                hash_password(new_pass),
                new_role,
                new_plan,
                datetime.datetime.now().isoformat()
            ))
            conn.commit()
            st.success("User Created")
        except:
            st.error("User already exists")

# ==============================
# CHANGE PASSWORD
# ==============================

st.markdown("---")
st.subheader("Change Password")

create_password = st.text_input(
    "New Password",
    type="password",
    key="create_user_password_input"
)

if st.button("Update Password"):
    c.execute("UPDATE users SET password=? WHERE username=?",
              (hash_password(new_password), st.session_state.username))
    conn.commit()
    st.success("Password Updated Successfully")
    # ==========================================================
# PART 2 – FILE ENGINE + ANALYSIS + STRATEGY + SMART BOT
# ==========================================================

import pandas as pd
import numpy as np
import plotly.express as px

# ==============================
# FILE UPLOAD (WITH LIMIT CHECK)
# ==============================

st.markdown("---")
st.header("Data Upload")

if uploads_used >= limits["uploads"]:
    st.error("Upload limit reached for your plan.")
else:
    uploaded_file = st.file_uploader(
        "Upload CSV / Excel File",
        type=["csv", "xlsx"]
    )

    if uploaded_file:

        # Increment upload counter
        c.execute("UPDATE users SET uploads_used = uploads_used + 1 WHERE username=?",
                  (st.session_state.username,))
        conn.commit()

        ext = uploaded_file.name.split(".")[-1].lower()

        if ext == "csv":
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("File Uploaded Successfully")
        st.dataframe(df.head())

        # Log activity
        c.execute("""
        INSERT INTO activity_log (username, action, timestamp)
        VALUES (?, ?, ?)
        """, (
            st.session_state.username,
            f"Uploaded file: {uploaded_file.name}",
            datetime.datetime.now().isoformat()
        ))
        conn.commit()

        # ==============================
        # SOCIAL MEDIA AUTO DETECTION
        # ==============================

        columns = [c.lower() for c in df.columns]

        dataset_type = "Generic Data"

        if "impressions" in columns and "clicks" in columns:
            dataset_type = "Paid Ads Data"

        elif "likes" in columns and "comments" in columns:
            dataset_type = "Organic Social Data"

        elif "keyword" in columns and "search_volume" in columns:
            dataset_type = "SEO Data"

        st.info(f"Detected Dataset Type: {dataset_type}")

        # ==============================
        # NUMERIC ANALYSIS
        # ==============================

        numeric_cols = df.select_dtypes(include=np.number).columns

        if len(numeric_cols) > 0:

            st.markdown("---")
            st.header("Performance Metrics")

            for col in numeric_cols:
                st.metric(f"{col} Average", round(df[col].mean(),2))

            fig = px.line(df[numeric_cols])
            st.plotly_chart(fig, use_container_width=True)

            # Trend Prediction
            st.subheader("AI Trend Prediction")

            col_choice = st.selectbox("Select Column for Prediction", numeric_cols)

            X = np.arange(len(df)).reshape(-1,1)
            y = df[col_choice].values.reshape(-1,1)

            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            model.fit(X, y)

            future = model.predict([[len(df)]])[0][0]

            st.success(f"Next Predicted Value: {round(float(future),2)}")
# ===================================
# MARKETING STRATEGY GENERATOR
# ===================================



# ===================================
# MARKETING STRATEGY GENERATOR
# ===================================

st.markdown("---")
st.header("Marketing Strategy Generator")

strategy_output = ""

if "revenue" in df.columns and "spend" in df.columns:

    df["ROAS"] = df["revenue"] / df["spend"]
    avg_roas = df["ROAS"].mean()

    if avg_roas < 1:
        strategy_output += "- Current ROAS is below profitability. Reallocate budget and improve creatives.\n"
    elif avg_roas < 2:
        strategy_output += "- Moderate ROAS. Focus on scaling best-performing campaigns.\n"
    else:
        strategy_output += "- Strong ROAS. Increase budget allocation strategically.\n"

elif "impressions" in df.columns and "clicks" in df.columns:
    strategy_output += "- Improve CTR by testing stronger hooks and creatives.\n"

elif "sessions" in df.columns:
    strategy_output += "- Focus on improving conversion rate and landing page optimization.\n"

else:
    strategy_output += "- General dataset detected. Focus on trend analysis and optimization.\n"

st.text_area("Strategic Recommendations", strategy_output, height=200)



# ===================================
# SMART STRATEGY ASSISTANT
# ===================================

st.markdown("---")
st.header("Smart Strategy Assistant")

user_question = st.text_input("Ask about your data", key="chat_input")

if user_question:
    st.info("AI assistant feature will be connected to OpenAI soon.")

        # ==============================
        # STRATEGY GENERATOR ENGINE
        # ==============================

       
        
            # ==========================================================
# PART 3 – ENTERPRISE PDF ENGINE PRO
# ==========================================================

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
import base64

# ==============================
# REPORT LANGUAGE MODE
# ==============================

st.markdown("---")
st.header("Enterprise Report")

report_language = st.selectbox(
    "Report Language",
    ["Arabic Only", "English Only", "Arabic + English"]
)

def generate_enterprise_pdf(df=None, strategy_text="", username="User", filename="File"):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    # Register Unicode font
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

    english_style = styles["Normal"]
    arabic_style = ParagraphStyle(
        name="ArabicStyle",
        parent=styles["Normal"],
        fontName="STSong-Light",
        fontSize=12
    )

    # ==============================
    # COVER
    # ==============================

    elements.append(Paragraph("MTSE Marketing Engine", styles["Heading1"]))
    elements.append(Spacer(1, 15))

    if report_language in ["English Only", "Arabic + English"]:
        elements.append(Paragraph("Enterprise Marketing Report", english_style))
        elements.append(Spacer(1, 10))

    if report_language in ["Arabic Only", "Arabic + English"]:
        elements.append(Paragraph("تقرير التسويق الاحترافي", arabic_style))
        elements.append(Spacer(1, 10))

    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Client: {username}", english_style))
    elements.append(Paragraph(f"File: {filename}", english_style))

    elements.append(PageBreak())

    # ==============================
    # EXECUTIVE SUMMARY
    # ==============================

    elements.append(Paragraph("Executive Summary", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    if report_language in ["English Only", "Arabic + English"]:
        elements.append(Paragraph(
            "This report analyzes performance data and provides marketing strategy recommendations.",
            english_style
        ))
        elements.append(Spacer(1, 10))

    if report_language in ["Arabic Only", "Arabic + English"]:
        elements.append(Paragraph(
            "يقوم هذا التقرير بتحليل البيانات وتقديم توصيات استراتيجية تسويقية.",
            arabic_style
        ))
        elements.append(Spacer(1, 10))

    elements.append(Spacer(1, 15))

    # ==============================
    # DATA METRICS TABLE
    # ==============================

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
            elements.append(Spacer(1, 20))

    # ==============================
    # STRATEGY SECTION
    # ==============================

    elements.append(Paragraph("Strategic Recommendations", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(strategy_text, english_style))
    elements.append(Spacer(1, 20))

    # ==============================
    # WATERMARK
    # ==============================

    def add_watermark(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 60)
        canvas.setFillGray(0.93)
        canvas.drawCentredString(A4[0]/2, A4[1]/2, "MTSE Marketing Engine")
        canvas.restoreState()

        canvas.setFont("Helvetica", 8)
        canvas.drawString(30, 20, "Generated by MTSE Marketing Engine")
        canvas.drawRightString(A4[0]-30, 20, "Confidential")

    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)

    buffer.seek(0)
    return buffer

# ==============================
# GENERATE REPORT BUTTON
# ==============================

if 'uploaded_file' in locals() and uploaded_file:

    if reports_used >= limits["reports"]:
        st.error("Report limit reached for your plan.")
    else:
        if st.button("Generate Enterprise PDF"):

            pdf_buffer = generate_enterprise_pdf(
                df=df if 'df' in locals() else None,
                strategy_text=strategy_output if 'strategy_output' in locals() else "",
                username=st.session_state.username,
                filename=uploaded_file.name
            )

            # Save to DB (Archive)
            c.execute("""
            INSERT INTO reports (username, file_name, created_at, summary, pdf_data)
            VALUES (?, ?, ?, ?, ?)
            """, (
                st.session_state.username,
                uploaded_file.name,
                datetime.datetime.now().isoformat(),
                strategy_output if 'strategy_output' in locals() else "",
                pdf_buffer.getvalue()
            ))
            conn.commit()

            # Increment report usage
            c.execute("UPDATE users SET reports_used = reports_used + 1 WHERE username=?",
                      (st.session_state.username,))
            conn.commit()

            st.success("Report Generated & Saved to Archive")

            st.download_button(
                "Download Report",
                data=pdf_buffer,
                file_name="MTSE_Report.pdf",
                mime="application/pdf"
            )

# ==============================
# REPORT ARCHIVE VIEW
# ==============================

st.markdown("---")
st.header("My Reports Archive")

user_reports = c.execute(
    "SELECT id, file_name, created_at FROM reports WHERE username=?",
    (st.session_state.username,)
).fetchall()

for r in user_reports:
    st.write(f"{r[1]} - {r[2]}")
    # ==========================================================
# PART 4 – SaaS ADVANCED SYSTEM
# ==========================================================

import calendar

# ==============================
# MONTHLY RESET SYSTEM
# ==============================

def reset_usage_if_new_month(username):
    c.execute("SELECT created_at FROM users WHERE username=?", (username,))
    user_data = c.fetchone()

    if user_data:
        created_date = datetime.datetime.fromisoformat(user_data[0])
        now = datetime.datetime.now()

        if created_date.month != now.month:
            c.execute("""
            UPDATE users 
            SET reports_used = 0,
                uploads_used = 0,
                created_at = ?
            WHERE username=?
            """, (now.isoformat(), username))
            conn.commit()

# Run reset check
reset_usage_if_new_month(st.session_state.username)

# ==============================
# BILLING READY FIELDS
# ==============================

# Add expiry_date column if not exists
try:
    c.execute("ALTER TABLE users ADD COLUMN expiry_date TEXT")
except:
    pass

# Add billing_status column
try:
    c.execute("ALTER TABLE users ADD COLUMN billing_status TEXT")
except:
    pass

conn.commit()

# ==============================
# ADMIN – ACTIVITY LOG VIEW
# ==============================

if st.session_state.role == "admin":

    st.markdown("---")
    st.header("System Activity Log")

    logs = c.execute("""
        SELECT username, action, timestamp 
        FROM activity_log
        ORDER BY timestamp DESC
        LIMIT 20
    """).fetchall()

    for log in logs:
        st.write(f"{log[2]} | {log[0]} → {log[1]}")

# ==============================
# ADMIN – PLAN MANAGEMENT
# ==============================

if st.session_state.role == "admin":

    st.markdown("---")
    st.header("Plan Management")

    all_users = c.execute("SELECT username, plan FROM users").fetchall()

    for user in all_users:
        col1, col2 = st.columns([2,2])
        col1.write(user[0])
        new_plan = col2.selectbox(
            f"Plan for {user[0]}",
            ["Starter", "Pro", "Business"],
            key=f"plan_{user[0]}"
        )

        if st.button(f"Update Plan {user[0]}"):
            c.execute("UPDATE users SET plan=? WHERE username=?",
                      (new_plan, user[0]))
            conn.commit()
            st.success(f"Plan updated for {user[0]}")

# ==============================
# ARCHIVE DOWNLOAD FROM DB
# ==============================

st.markdown("---")
st.header("Download Archived Reports")

archived_reports = c.execute("""
    SELECT id, file_name, pdf_data
    FROM reports
    WHERE username=?
""", (st.session_state.username,)).fetchall()

for report in archived_reports:

    report_id, file_name, pdf_blob = report

    st.download_button(
        label=f"Download {file_name}",
        data=pdf_blob,
        file_name=f"{file_name}_archived.pdf",
        mime="application/pdf",
        key=f"download_{report_id}"
    )

# ==============================
# USAGE DASHBOARD (VISUAL)
# ==============================

st.markdown("---")
st.header("Usage Analytics")

usage_data = {
    "Reports Used": reports_used,
    "Uploads Used": uploads_used
}

usage_df = pd.DataFrame(
    list(usage_data.items()),
    columns=["Metric", "Value"]
)

fig_usage = px.bar(usage_df, x="Metric", y="Value", title="Current Usage")
st.plotly_chart(fig_usage, use_container_width=True)

# ==============================
# BILLING STATUS DISPLAY
# ==============================

st.markdown("---")
st.header("Subscription Status")

c.execute("SELECT billing_status, expiry_date FROM users WHERE username=?",
          (st.session_state.username,))
billing_info = c.fetchone()

billing_status = billing_info[0] if billing_info else None
expiry_date = billing_info[1] if billing_info else None

st.write("Billing Status:", billing_status if billing_status else "Active")
st.write("Expiry Date:", expiry_date if expiry_date else "Not Set")

# ==============================
# PLAN UPGRADE SIMULATION
# ==============================

st.markdown("---")
st.header("Upgrade Plan (Simulation)")

upgrade_plan = st.selectbox("Choose Plan", ["Starter", "Pro", "Business"])

if st.button("Upgrade Plan"):
    c.execute("""
        UPDATE users 
        SET plan=?, billing_status='Active', expiry_date=?
        WHERE username=?
    """, (
        upgrade_plan,
        (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat(),
        st.session_state.username
    ))
    conn.commit()

    st.success("Plan upgraded successfully (Simulation Mode)")
    # ==========================================================
# PART 5 – GPT AI ENGINE (Advanced Narrative Generator)
# ==========================================================

import os
import openai

# Load API Key
openai.api_key = st.secrets.get("OPENAI_API_KEY", None)

def generate_ai_strategy(df=None, dataset_type="Generic"):

    if openai.api_key is None:
        return "AI Integration not configured."

    summary_data = ""

    if df is not None:
        numeric_cols = df.select_dtypes(include=np.number).columns
        for col in numeric_cols:
            summary_data += f"{col} average: {round(df[col].mean(),2)}\n"

    prompt = f"""
    You are a senior global marketing strategist.

    Dataset Type: {dataset_type}

    Performance Summary:
    {summary_data}

    Generate:
    - Executive Summary
    - Funnel Diagnosis
    - Budget Allocation Strategy
    - 30-Day Marketing Plan
    - Scaling Recommendation

    Write professionally for international markets.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert marketing strategist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response["choices"][0]["message"]["content"]

    except Exception as e:
        return f"AI Error: {e}"

# ==============================
# AI STRATEGY BUTTON
# ==============================

st.markdown("---")
st.header("AI Strategic Intelligence")

if 'df' in locals() and df is not None:

    if st.button("Generate AI Full Marketing Strategy"):

        ai_output = generate_ai_strategy(df, dataset_type)

        st.markdown("### AI Generated Strategy")
        st.write(ai_output)

        # Log activity
        c.execute("""
        INSERT INTO activity_log (username, action, timestamp)
        VALUES (?, ?, ?)
        """, (
            st.session_state.username,
            "Generated AI Strategy",
            datetime.datetime.now().isoformat()
        ))
        conn.commit()

# ==============================
# AI CHATBOT (REAL GPT)
# ==============================

st.markdown("---")
st.header("AI Chat Assistant (Advanced)")

chat_input = st.text_input("Ask the AI about your marketing data")

if chat_input and openai.api_key:

    context_data = ""

    if 'df' in locals() and df is not None:
        context_data = df.head().to_string()

    chat_prompt = f"""
    User Question: {chat_input}

    Data Context:
    {context_data}

    Answer as a professional marketing consultant.
    """

    try:
        chat_response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a marketing expert."},
                {"role": "user", "content": chat_prompt}
            ]
        )

        st.success(chat_response["choices"][0]["message"]["content"])

    except Exception as e:
        st.error(f"AI Error: {e}")
        # ==========================================================
# PART 6 – STRIPE + TEAM ACCOUNTS + WHITE LABEL
# ==========================================================

import stripe

stripe.api_key = st.secrets.get("STRIPE_SECRET_KEY", None)

# ==============================
# DATABASE EXTENSIONS
# ==============================

# Add company column
try:
    c.execute("ALTER TABLE users ADD COLUMN company TEXT")
except:
    pass

# Teams table
c.execute("""
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT,
    owner TEXT
)
""")

conn.commit()

# ==============================
# STRIPE CHECKOUT SIMULATION
# ==============================

st.markdown("---")
st.header("Subscription Billing")

PLAN_PRICING = {
    "Starter": 29,
    "Pro": 99,
    "Business": 299
}

if stripe.api_key:

    selected_plan = st.selectbox("Choose Plan to Subscribe", ["Starter","Pro","Business"])
    price = PLAN_PRICING[selected_plan]

    if st.button("Proceed to Payment"):

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"{selected_plan} Plan"
                        },
                        "unit_amount": price * 100,
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

            st.success("Redirect to payment:")
            st.write(checkout_session.url)

        except Exception as e:
            st.error(f"Stripe Error: {e}")

else:
    st.info("Stripe not configured yet.")

# ==============================
# TEAM ACCOUNT SYSTEM
# ==============================

st.markdown("---")
st.header("Team Management")

if st.session_state.role == "admin":

    company_name = st.text_input("Company Name")

    if st.button("Create Team"):
        c.execute("""
        INSERT INTO teams (company, owner)
        VALUES (?, ?)
        """, (company_name, st.session_state.username))
        conn.commit()
        st.success("Team Created")

    st.subheader("Assign User to Company")

    assign_user = st.text_input("Username to Assign")

    if st.button("Assign to Company"):
        c.execute("UPDATE users SET company=? WHERE username=?",
                  (company_name, assign_user))
        conn.commit()
        st.success("User Assigned")

# ==============================
# WHITE LABEL MODE
# ==============================

st.markdown("---")
st.header("White Label Mode")

white_label_name = st.text_input("Brand Name")
white_label_logo = st.file_uploader("Upload Logo", type=["png","jpg"])

if white_label_name:
    st.markdown(f"### {white_label_name}")

if white_label_logo:
    st.image(white_label_logo, width=120)

# ==============================
# MULTI-COMPANY DATA FILTER
# ==============================

if st.session_state.role != "admin":

    c.execute("SELECT company FROM users WHERE username=?",
              (st.session_state.username,))
    user_company = c.fetchone()

    if user_company and user_company[0]:
        st.info(f"Company Account: {user_company[0]}")
        # ==========================================================
# PART 7 – ENTERPRISE EXPANSION LAYER
# ==========================================================

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==============================
# CRM TABLE
# ==============================

c.execute("""
CREATE TABLE IF NOT EXISTS crm_leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    company TEXT,
    status TEXT,
    created_at TEXT
)
""")

conn.commit()

# ==============================
# CRM SYSTEM
# ==============================

st.markdown("---")
st.header("Mini CRM System")

lead_name = st.text_input("Lead Name")
lead_email = st.text_input("Lead Email")
lead_company = st.text_input("Company")

if st.button("Add Lead"):
    c.execute("""
    INSERT INTO crm_leads (name,email,company,status,created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
        lead_name,
        lead_email,
        lead_company,
        "New",
        datetime.datetime.now().isoformat()
    ))
    conn.commit()
    st.success("Lead Added")

leads = c.execute("SELECT name,email,company,status FROM crm_leads").fetchall()

for lead in leads:
    st.write(lead)

# ==============================
# INVOICE GENERATOR
# ==============================

st.markdown("---")
st.header("Invoice Generator")

invoice_client = st.text_input("Client Name")
invoice_amount = st.number_input("Amount", min_value=0)

def generate_invoice_pdf(client, amount):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("MTSE Marketing Engine", styles["Heading1"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Invoice To: {client}", styles["Normal"]))
    elements.append(Paragraph(f"Amount: ${amount}", styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Thank you for your business.", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

if st.button("Generate Invoice"):
    invoice_pdf = generate_invoice_pdf(invoice_client, invoice_amount)
    st.download_button(
        "Download Invoice",
        data=invoice_pdf,
        file_name="invoice.pdf",
        mime="application/pdf"
    )

# ==============================
# EMAIL AUTOMATION READY
# ==============================

st.markdown("---")
st.header("Email Campaign Simulation")

email_subject = st.text_input("Subject")
email_body = st.text_area("Email Content")

if st.button("Simulate Send Email"):
    st.success("Email campaign triggered (Simulation Mode)")

# ==============================
# WHITE LABEL DOMAIN READY
# ==============================

st.markdown("---")
st.header("White Label Domain Settings")

custom_domain = st.text_input("Custom Domain")

if custom_domain:
    st.info(f"Domain {custom_domain} linked (Simulation Mode)")

# ==============================
# PREMIUM UI ENHANCEMENT
# ==============================

st.markdown("""
<style>
button {
    background-color: #facc15 !important;
    color: black !important;
    font-weight: bold;
    border-radius: 8px;
}
.stTextInput > div > div > input {
    background-color: #1e293b;
    color: white;
}
</style>
""", unsafe_allow_html=True)






