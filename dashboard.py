# ==========================================================
# MTSE Marketing Engine - SaaS Edition v1.0 (PART 1)
# Core Architecture + Auth + Plans + Usage + Admin
# ==========================================================

import streamlit as st
st.set_page_config(
    page_title="MTSE Marketing Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
from pages import dashboard_page
from pages import analytics_page
from pages import ai_engine_page
from pages import reports_page
from pages import users_page
from pages import billing_page
from pages import settings_page
with st.sidebar:
    st.markdown("## 🚀 MTSE")
    st.markdown("### Navigation")
    st.markdown("---")

    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"

    def nav_button(label, icon):
        if st.button(f"{icon}  {label}", use_container_width=True):
            st.session_state.page = label

    nav_button("Dashboard", "🏠")
    nav_button("Analytics", "📊")
    nav_button("AI Engine", "🤖")
    nav_button("Reports", "📁")
    nav_button("Users", "👥")
    nav_button("Billing", "💳")
    nav_button("Settings", "⚙")
    page = st.session_state.page

if page == "Dashboard":
    dashboard_page.render()
elif page == "Analytics":
    analytics_page.render()
elif page == "AI Engine":
    ai_engine_page.render()
elif page == "Reports":
    reports_page.render()
elif page == "Users":
    users_page.render()
elif page == "Billing":
    billing_page.render()
elif page == "Settings":
    settings_page.render()
   











































