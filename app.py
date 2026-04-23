"""
Rate Calculator — home page.
"""

import streamlit as st

st.set_page_config(
    page_title="Rate Calculator",
    page_icon="🧮",
    layout="wide",
)

st.title("🧮 Rate Calculator")
st.markdown("**2024/25 tax year — UK contracting & employment**")

st.markdown("---")

st.markdown(
    """
    Use the navigation on the left to switch between calculators.

    | Calculator | Description |
    |---|---|
    | **Umbrella** | Inside IR35 — agency day rate processed via an umbrella company |
    | **Salaried** | Full-time direct employment — gross salary to net take-home |
    | **Ltd Co** | Outside IR35 — invoicing via your own limited company *(coming soon)* |
    """
)

st.markdown("---")
st.caption(
    "Figures are indicative only. Tax rates and thresholds based on 2024/25 HMRC published rates. "
    "Not financial advice — verify with your accountant."
)
