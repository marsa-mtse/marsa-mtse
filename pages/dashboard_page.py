import streamlit as st

def render():
    st.title("📊 Dashboard")

    st.markdown("### Usage Overview")

    col1, col2 = st.columns(2)

    col1.metric("Reports Used", "12 / 100")
    col2.metric("Uploads Used", "5 / 50")

    st.markdown("---")
    st.subheader("Admin Panel")
    st.write("Welcome to MTSE Dashboard 🚀")
