import streamlit as st

from streamlit_app.components.kpis import show_kpis

st.title("Dashboard")
show_kpis()