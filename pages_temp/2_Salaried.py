"""
Salaried Rate Calculator — Full-time employment.
"""

import streamlit as st
from salaried_calculator import calculate, SalariedAssumptions

st.set_page_config(
    page_title="Salaried Calculator",
    page_icon="🧮",
    layout="wide",
)

st.title("Full-Time Salaried Calculator")
st.caption("Direct employment — PAYE. 2024/25 tax year.")

# ── Salary input ──────────────────────────────────────────────────────────────
col_input, col_gap = st.columns([1, 2])
with col_input:
    annual_salary = st.number_input(
        "Annual Salary (£/yr)",
        min_value=10_000,
        max_value=500_000,
        value=98_500,
        step=500,
        help="Your gross contracted salary before any deductions.",
    )

# ── Assumptions expander ──────────────────────────────────────────────────────
with st.expander("Assumptions — click to edit"):
    st.markdown("**Working pattern**")
    c1, c2, c3 = st.columns(3)
    with c1:
        days_per_week = st.number_input("Days/week", value=5.0, step=0.5)
    with c2:
        weeks_per_year = st.number_input("Weeks/year", value=46, step=1)
    with c3:
        hours_per_day = st.number_input("Hours/day", value=7.5, step=0.5)

    st.markdown("**Pension**")
    c1, c2, c3 = st.columns(3)
    with c1:
        pension_type = st.selectbox(
            "Pension scheme type",
            ["Relief at source", "Net pay arrangement", "Salary sacrifice"],
            index=0,
            help="Relief at source: pension deducted after tax, HMRC tops up at 20%. Net pay: deducted before tax and NI. Salary sacrifice: gross salary reduced, saves employee and employer NI.",
        )
    with c2:
        employee_pension_rate = st.number_input(
            "Employee contribution (%)", value=13.5, step=0.5, format="%.1f"
        ) / 100
    with c3:
        employer_pension_rate = st.number_input(
            "Employer contribution (%)", value=28.97, step=0.5, format="%.2f"
        ) / 100

    employer_passes_ni = False
    if pension_type == "Salary sacrifice":
        employer_passes_ni = st.checkbox("Employer passes NI saving to pension?", value=False)

    st.markdown("**Other employer costs**")
    c1, c2, c3 = st.columns(3)
    with c1:
        sick_pay_rate = st.number_input(
            "Employer sick pay liability (% of salary)", value=2.0, step=0.5, format="%.1f",
            help="Approximate cost of contractual sick pay entitlement as a % of salary. 2% ≈ 5 days full pay per year.",
        ) / 100

# ── Build assumptions & calculate ────────────────────────────────────────────
a = SalariedAssumptions(
    days_per_week=days_per_week,
    weeks_per_year=weeks_per_year,
    hours_per_day=hours_per_day,
    pension_scheme_type=pension_type,
    employee_pension_rate=employee_pension_rate,
    employer_pension_rate=employer_pension_rate,
    employer_passes_ni_saving_to_pension=employer_passes_ni,
    employer_sick_pay_rate=sick_pay_rate,
)
r = calculate(annual_salary, a)

# ── Sidebar — key metrics ─────────────────────────────────────────────────────
with st.sidebar:
    st.header("Key Metrics")
    st.metric("Annual net take-home", f"£{r.annual_net:,.0f}")
    st.metric("Monthly net take-home", f"£{r.monthly_net:,.0f}")
    st.metric("Daily net equivalent", f"£{r.daily_net:,.2f}")
    st.metric("Hourly net equivalent", f"£{r.hourly_net:,.2f}")
    st.divider()
    st.metric("Effective tax rate", f"{r.effective_tax_rate:.1%}",
              help="Income tax + employee NI + pension as a % of gross salary.")
    st.metric("Equivalent day rate", f"£{r.equivalent_day_rate:,.2f}",
              help="Gross salary ÷ working days per year.")
    st.divider()
    st.metric("Total cost to employer", f"£{r.total_cost_to_employer:,.0f}")
    st.metric("Breakeven contractor day rate", f"£{r.breakeven_day_rate:,.2f}",
              help="The contractor day rate that costs the client the same as employing you at this salary.")

# ── Full breakdown ────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Full Breakdown")

left, right = st.columns(2)

with left:
    st.markdown("**Step 1 — Gross salary**")
    for label, value, is_deduction in [
        ("Gross annual salary", annual_salary, False),
        ("Equivalent day rate", r.equivalent_day_rate, False),
    ]:
        ca, cb = st.columns([3, 1])
        style = "font-weight: bold;"
        ca.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
        cb.markdown(f"<span style='{style}'>£{value:,.2f}</span>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("**Step 2 — Pre-tax deductions**")
    for label, value, is_deduction in [
        ("Gross salary", annual_salary, False),
        ("Less: Employee pension (pre-tax)", -r.employee_pension_pretax, True),
        ("= Gross taxable pay", r.gross_taxable_pay, False),
    ]:
        ca, cb = st.columns([3, 1])
        style = "color: #cc0000;" if is_deduction else "font-weight: bold;"
        ca.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
        cb.markdown(f"<span style='{style}'>£{value:,.2f}</span>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("**Step 3 — Income tax & NI**")
    for label, value, is_deduction in [
        ("Gross taxable pay", r.gross_taxable_pay, False),
        ("Less: Income tax (basic rate)", -r.income_tax_basic, True),
        ("Less: Income tax (higher rate)", -r.income_tax_higher, True),
        ("Less: Income tax (additional rate)", -r.income_tax_additional, True),
        ("Less: Employee NI (standard)", -r.employee_ni_standard, True),
        ("Less: Employee NI (above UEL)", -r.employee_ni_above_uel, True),
        ("Less: Employee pension (post-tax)", -r.employee_pension_posttax, True),
        ("= Net take-home (annual)", r.annual_net, False),
    ]:
        ca, cb = st.columns([3, 1])
        style = "color: #cc0000;" if is_deduction else "font-weight: bold;"
        ca.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
        cb.markdown(f"<span style='{style}'>£{value:,.2f}</span>", unsafe_allow_html=True)

with right:
    st.markdown("**Pension memo**")
    for label, value in [
        ("Your pension contribution", r.employee_pension_contribution),
        ("HMRC basic rate top-up", r.hmrc_basic_rate_topup),
        ("Employer NI saving to pension", r.employer_ni_saving_to_pension),
        ("Total pension pot funded", r.total_pension_pot),
    ]:
        ca, cb = st.columns([3, 1])
        bold = "font-weight: bold;" if "Total" in label else ""
        ca.markdown(f"<span style='{bold}'>{label}</span>", unsafe_allow_html=True)
        cb.markdown(f"<span style='{bold}'>£{value:,.2f}</span>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("**Cost to employer**")
    for label, value in [
        ("Gross salary", annual_salary),
        ("  Employer NI", r.employer_ni),
        ("  Employer pension contribution", r.employer_pension),
        ("  Employer sick pay liability", r.employer_sick_pay_liability),
        ("Total cost to employer", r.total_cost_to_employer),
        ("Breakeven contractor day rate", r.breakeven_day_rate),
    ]:
        ca, cb = st.columns([3, 1])
        bold = "font-weight: bold;" if "Total" in label or "Breakeven" in label or label == "Gross salary" else ""
        ca.markdown(f"<span style='{bold}'>{label}</span>", unsafe_allow_html=True)
        cb.markdown(f"<span style='{bold}'>£{value:,.2f}</span>", unsafe_allow_html=True)

# ── Tax summary ───────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Tax & Deductions Summary")
s1, s2, s3, s4, s5 = st.columns(5)
s1.metric("Income tax", f"£{r.income_tax_paid:,.0f}")
s2.metric("Employee NI", f"£{r.employee_ni_paid:,.0f}")
s3.metric("Your pension", f"£{r.employee_pension_contribution:,.0f}")
s4.metric("Employer pension", f"£{r.employer_pension_contribution:,.0f}")
s5.metric("Employer NI", f"£{r.employer_ni:,.0f}")

st.markdown("---")
st.caption(
    "Figures are indicative only. Tax rates and thresholds based on 2024/25 HMRC published rates. "
    "Not financial advice — verify with your accountant."
)
