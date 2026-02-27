import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from datetime import datetime
import os

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="MTSE Analytics", layout="wide")

# ----------------------------
# THEME
# ----------------------------
st.markdown("""
<style>
body {background-color:#f4f4f4;}
h1,h2,h3 {color:#2c2c2c;}
.stButton>button {
background:#5a5a5a;
color:white;
border-radius:6px;
}
section[data-testid="stSidebar"] {
background-color:#eaeaea;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# LOGO HEADER
# ----------------------------
st.markdown("""
# 📊 MTSE Analytics  
### Data & Marketing Analytics Platform | منصة تحليل البيانات
""")

# ----------------------------
# SESSION INIT
# ----------------------------
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "Admin@2026", "plan": "Pro Max", "role": "Admin"}
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ----------------------------
# AUTH
# ----------------------------
def login():
    st.sidebar.subheader("Login")
    u = st.sidebar.text_input("Username")
    p = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if u in st.session_state.users and st.session_state.users[u]["password"] == p:
            st.session_state.logged_in = True
            st.session_state.current_user = u
        else:
            st.sidebar.error("Wrong Credentials")

def register():
    st.sidebar.subheader("Create Account")
    new_u = st.sidebar.text_input("New Username")
    new_p = st.sidebar.text_input("New Password", type="password")
    plan = st.sidebar.selectbox("Plan", ["Starter","Pro","Pro Max"])
    if st.sidebar.button("Register"):
        st.session_state.users[new_u] = {"password":new_p,"plan":plan,"role":"User"}
        st.sidebar.success("Account Created")

if not st.session_state.logged_in:
    login()
    register()
    st.stop()

# ----------------------------
# USER INFO
# ----------------------------
user = st.session_state.current_user
plan = st.session_state.users[user]["plan"]
role = st.session_state.users[user]["role"]

st.success(f"Welcome {user} | Plan: {plan} | Role: {role}")

# ----------------------------
# FILE UPLOAD
# ----------------------------
file = st.file_uploader("Upload CSV File", type=["csv"])

if file:
    df = pd.read_csv(file)
    st.dataframe(df.head())

    numeric_cols = df.select_dtypes(include=np.number).columns

    if len(numeric_cols) > 0:

        st.subheader("Smart Auto Analysis")

        insights = []

        for col in numeric_cols:
            avg = df[col].mean()
            max_v = df[col].max()
            min_v = df[col].min()

            st.write(f"### {col}")
            st.write("Average:", round(avg,2))
            st.write("Max:", max_v)
            st.write("Min:", min_v)

            if avg > df[col].median():
                insights.append(f"{col} performing above median.")
            else:
                insights.append(f"{col} below expected trend.")

        # Visualization
        selected = st.selectbox("Visualize Column", numeric_cols)
        fig = px.line(df, y=selected, title=f"{selected} Trend")
        st.plotly_chart(fig, use_container_width=True)

        # Trend Prediction (Pro / Pro Max)
        if plan in ["Pro","Pro Max"]:
            st.subheader("AI Trend Prediction")
            X = np.array(range(len(df))).reshape(-1,1)
            y = df[selected].values
            model = LinearRegression()
            model.fit(X,y)
            future = model.predict([[len(df)+1]])
            st.write("Next Predicted Value:", round(float(future),2))

        # ---------------- PDF ----------------
        def generate_pdf():
            name = "MTSE_Report.pdf"
            doc = SimpleDocTemplate(name, pagesize=A4)
            elements = []

            style = ParagraphStyle(name="style", fontSize=12, textColor=colors.black)

            elements.append(Paragraph("<b>MTSE Analytics Report</b>", style))
            elements.append(Spacer(1,12))
            elements.append(Paragraph(f"File: {file.name}", style))
            elements.append(Spacer(1,12))
            elements.append(Paragraph(f"Generated For: {user}", style))
            elements.append(Spacer(1,12))

            for i in insights:
                elements.append(Paragraph(i, style))
                elements.append(Spacer(1,6))

            elements.append(Spacer(1,30))
            elements.append(Paragraph("Powered by MTSE Analytics", style))

            doc.build(elements)
            return name

        if plan in ["Pro","Pro Max"]:
            if st.button("Generate Professional PDF"):
                path = generate_pdf()
                with open(path,"rb") as f:
                    st.download_button("Download Report", f, file_name="MTSE_Report.pdf")

# ----------------------------
# ADMIN PANEL
# ----------------------------
if role == "Admin":
    st.subheader("Admin Control Panel")
    st.write(st.session_state.users)

# ----------------------------
# PRICING
# ----------------------------
st.markdown("""
---

## Pricing Plans

**Starter – 499 EGP / month**  
Basic Analysis  

**Pro – 1499 EGP / month**  
AI Insights + PDF  

**Pro Max – Custom**  
Full AI + Multi User + Advanced Features  

---

📧 marsatouch@gmail.com  
📱 WhatsApp Group:  
https://chat.whatsapp.com/BepZmZWVy01EFmU6vrhjo1

""")
