import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import hashlib
from sklearn.linear_model import LinearRegression
import plotly.express as px
import plotly.graph_objects as go
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="MTSE Analytics", layout="wide")

# =====================================================
# PLATFORM WATERMARK (Medium Visibility)
# =====================================================
st.markdown("""
<style>
.stApp::before {
    content: "MTSE Analytics";
    position: fixed;
    top: 45%;
    left: 18%;
    font-size: 110px;
    color: rgba(0,0,0,0.07);
    transform: rotate(-30deg);
    pointer-events: none;
}
.stApp { background-color: #F4F1EC; }
h1,h2,h3 { color:#2C2C2C; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# DATABASE (SQLite)
# =====================================================
conn = sqlite3.connect("mtse.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
username TEXT PRIMARY KEY,
password TEXT,
role TEXT,
plan TEXT
)
""")
conn.commit()

admin_pass = hashlib.sha256("SQlite@2026".encode()).hexdigest()
c.execute("SELECT * FROM users WHERE username='admin'")
if not c.fetchone():
    c.execute("INSERT INTO users VALUES (?,?,?,?)",
              ("admin", admin_pass, "Admin", "Pro Max"))
    conn.commit()

# =====================================================
# AUTH
# =====================================================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

if "logged" not in st.session_state:
    st.session_state.logged = False

if not st.session_state.logged:
    st.sidebar.title("Login")

    u = st.sidebar.text_input("Username")
    p = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (u, hash_pass(p)))
        user = c.fetchone()
        if user:
            st.session_state.logged = True
            st.session_state.username = user[0]
            st.session_state.role = user[2]
            st.session_state.plan = user[3]
        else:
            st.sidebar.error("Wrong Credentials")

    st.stop()

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<h1>📊 MTSE Analytics</h1>
<h4 style='color:gray;'>Data & Marketing Intelligence Platform</h4>
""", unsafe_allow_html=True)

st.success(f"Welcome {st.session_state.username} | Plan: {st.session_state.plan}")

# =====================================================
# FILE UPLOAD
# =====================================================
file = st.file_uploader("Upload CSV File", type=["csv"])

if file:

    df = pd.read_csv(file)
    st.subheader("Data Preview")
    st.dataframe(df.head())

    numeric_cols = df.select_dtypes(include=np.number).columns

    if len(numeric_cols) > 0:

        st.subheader("Smart Auto Analysis")

        insights = []

        for col in numeric_cols:
            avg = df[col].mean()
            median = df[col].median()

            if avg > median:
                insights.append(f"{col} shows positive growth trend.")
            else:
                insights.append(f"{col} requires optimization.")

        col_select = st.selectbox("Select Metric", numeric_cols)

        fig = px.line(df, y=col_select)
        st.plotly_chart(fig, use_container_width=True)

        # ================= AI Prediction =================
        st.subheader("AI Trend Prediction")

        X = np.arange(len(df)).reshape(-1,1)
        y = df[col_select].values.reshape(-1,1)

        model = LinearRegression()
        model.fit(X,y)

        future_value = float(model.predict([[len(df)]])[0][0])

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=list(range(len(df))),
                                  y=df[col_select],
                                  mode='lines',
                                  name='Actual'))
        fig2.add_trace(go.Scatter(x=[len(df)],
                                  y=[future_value],
                                  mode='markers',
                                  marker=dict(size=12),
                                  name='Predicted'))

        st.plotly_chart(fig2, use_container_width=True)
        st.success(f"Next Predicted Value: {round(future_value,2)}")

        # ================= AI BOT =================
        st.subheader("🤖 Ask MTSE AI")

        question = st.text_input("Ask about your data")

        if question:
            if "best" in question.lower():
                st.write("Highest Value:", df[col_select].max())
            elif "average" in question.lower():
                st.write("Average:", round(df[col_select].mean(),2))
            else:
                st.write("AI Insight:", insights)

        # ================= PROFESSIONAL PDF =================
        def generate_pdf():
            filename = "MTSE_Analytics_Report.pdf"
            doc = SimpleDocTemplate(filename, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph("<b>MTSE Analytics Report</b>", styles["Heading1"]))
            elements.append(Spacer(1,12))
            elements.append(Paragraph(f"Client: {st.session_state.username}", styles["Normal"]))
            elements.append(Paragraph(f"File: {file.name}", styles["Normal"]))
            elements.append(Paragraph(f"Date: {datetime.now().strftime('%d %B %Y')}", styles["Normal"]))
            elements.append(Spacer(1,20))

            elements.append(Paragraph("Executive Summary", styles["Heading2"]))
            elements.append(Spacer(1,10))

            for i in insights:
                elements.append(Paragraph(i, styles["Normal"]))
                elements.append(Spacer(1,6))

            data = [["Metric","Average"]]
            for col in numeric_cols:
                data.append([col, round(df[col].mean(),2)])

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#EAE6DF")),
                ('GRID',(0,0),(-1,-1),0.5,colors.grey)
            ]))

            elements.append(Spacer(1,20))
            elements.append(table)

            def watermark(canvas, doc):
                canvas.saveState()
                canvas.setFont("Helvetica", 60)
                canvas.setFillGray(0.85)
                canvas.drawCentredString(A4[0]/2, A4[1]/2, "MTSE Analytics")
                canvas.restoreState()

                canvas.setFont("Helvetica", 9)
                canvas.drawString(30, 20, "Powered by MTSE Analytics Platform")
                canvas.drawRightString(A4[0]-30, 20, "Confidential")

            doc.build(elements, onFirstPage=watermark, onLaterPages=watermark)
            return filename

        if st.button("Generate Professional PDF Report"):
            pdf_file = generate_pdf()
            with open(pdf_file, "rb") as f:
                st.download_button("Download Report", f, file_name=pdf_file)

# =====================================================
# ADMIN PANEL
# =====================================================
if st.session_state.role == "Admin":
    st.markdown("---")
    st.subheader("Admin Control Panel")
    c.execute("SELECT username, role, plan FROM users")
    users = c.fetchall()
    admin_df = pd.DataFrame(users, columns=["Username","Role","Plan"])
    st.dataframe(admin_df)
