"""
Umbrella Rate Calculator — Streamlit app.
"""

import streamlit as st
from calculator import calculate, UmbrellaAssumptions

st.set_page_config(
    page_title="Umbrella Rate Calculator",
    page_icon="🧮",
    layout="wide",
)

st.title("Umbrella Rate Calculator")
st.caption("Inside IR35 — Umbrella Company. 2024/25 tax year.")

# ── Main input ────────────────────────────────────────────────────────────────
col_input, col_gap = st.columns([1, 2])
with col_input:
    day_rate = st.number_input(
        "Day Rate (£/day)",
        min_value=100,
        max_value=2_000,
        value=550,
        step=25,
        help="The rate you invoice via the agency / umbrella.",
    )

# ── Assumption overrides ──────────────────────────────────────────────────────
with st.expander("Assumptions — click to edit"):
    st.markdown("**Working pattern**")
    c1, c2, c3 = st.columns(3)
    with c1:
        days_per_week = st.number_input("Days/week", value=5.0, step=0.5)
    with c2:
        weeks_per_year = st.number_input("Weeks/year", value=46, step=1)
    with c3:
        hours_per_day = st.number_input("Hours/day", value=7.5, step=0.5)

    st.markdown("**Umbrella costs**")
    c1, c2 = st.columns(2)
    with c1:
        umbrella_margin = st.number_input("Umbrella margin (£/week)", value=25, step=5)
    with c2:
        include_levy = st.checkbox("Apprenticeship Levy charged?", value=True, help="Does the Umbrella company include an apprenticeship levy?")

    st.markdown("**Pension**")
    c1, c2, c3 = st.columns(3)
    with c1:
        pension_type = st.selectbox(
            "Pension scheme type",
            ["Net pay arrangement", "Relief at source", "Salary sacrifice"],
            index=0,
        )
    with c2:
        employee_pension_rate = st.number_input(
            "Employee contribution (%)", value=5.0, step=0.5, format="%.1f"
        ) / 100
    with c3:
        employer_pension_rate = st.number_input(
            "Employer contribution (%)", value=3.0, step=0.5, format="%.1f"
        ) / 100

    employer_passes_ni = False
    if pension_type == "Salary sacrifice":
        employer_passes_ni = st.checkbox("Employer passes NI saving to pension?", value=False)

# ── Build assumptions & calculate ─────────────────────────────────────────────
a = UmbrellaAssumptions(
    days_per_week=days_per_week,
    weeks_per_year=weeks_per_year,
    hours_per_day=hours_per_day,
    umbrella_margin_per_week=umbrella_margin,
    apprenticeship_levy_rate=0.005 if include_levy else 0.0,
    pension_scheme_type=pension_type,
    employee_pension_rate=employee_pension_rate,
    employer_pension_rate=employer_pension_rate,
    employer_passes_ni_saving_to_pension=employer_passes_ni,
)
r = calculate(day_rate, a)

# ── Key metrics ───────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Net Take-Home")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Annual", f"£{r.annual_net:,.0f}")
m2.metric("Monthly", f"£{r.monthly_net:,.0f}")
m3.metric("Daily equivalent", f"£{r.daily_net:,.2f}")
m4.metric("Effective tax rate", f"{r.effective_tax_rate:.1%}")

# ── Calculation waterfall ─────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Full Breakdown")

left, right = st.columns(2)

with left:
    st.markdown("**Step 1 — Umbrella deductions**")
    waterfall = [
        ("Gross contract income", r.annual_gross_contract_income, False),
        ("Less: Umbrella margin", -r.umbrella_margin_annual, True),
        ("Less: Employer NI", -r.employer_ni, True),
        ("Less: Apprenticeship Levy", -r.apprenticeship_levy, True),
        ("= Gross PAYE salary", r.gross_paye_salary, False),
    ]
    for label, value, is_deduction in waterfall:
        col_a, col_b = st.columns([3, 1])
        style = "color: #cc0000;" if is_deduction else "font-weight: bold;"
        col_a.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
        col_b.markdown(f"<span style='{style}'>£{value:,.2f}</span>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("**Step 2 — Pre-tax deductions**")
    for label, value, is_deduction in [
        ("Gross PAYE salary", r.gross_paye_salary, False),
        ("Less: Employee pension (pre-tax)", -r.employee_pension_pretax, True),
        ("= Gross taxable pay", r.gross_taxable_pay, False),
    ]:
        col_a, col_b = st.columns([3, 1])
        style = "color: #cc0000;" if is_deduction else "font-weight: bold;"
        col_a.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
        col_b.markdown(f"<span style='{style}'>£{value:,.2f}</span>", unsafe_allow_html=True)

with right:
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
        col_a, col_b = st.columns([3, 1])
        style = "color: #cc0000;" if is_deduction else "font-weight: bold;"
        col_a.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
        col_b.markdown(f"<span style='{style}'>£{value:,.2f}</span>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("**Cost to client**")
    for label, value in [
        ("Gross contract fee", r.annual_gross_contract_income),
        ("  Of which: umbrella margin", r.umbrella_margin_annual),
        ("  Of which: employer NI", r.employer_ni),
        ("  Of which: apprenticeship levy", r.apprenticeship_levy),
        ("  Of which: employer pension", r.employer_pension_annual),
        ("Total cost to client", r.total_cost_to_client),
    ]:
        col_a, col_b = st.columns([3, 1])
        bold = "font-weight: bold;" if "Total" in label or label == "Gross contract fee" else ""
        col_a.markdown(f"<span style='{bold}'>{label}</span>", unsafe_allow_html=True)
        col_b.markdown(f"<span style='{bold}'>£{value:,.2f}</span>", unsafe_allow_html=True)

# ── Tax summary ───────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Tax & Deductions Summary")
s1, s2, s3, s4, s5 = st.columns(5)
s1.metric("Income tax", f"£{r.income_tax_paid:,.0f}")
s2.metric("Employee NI", f"£{r.employee_ni_paid:,.0f}")
s3.metric("Umbrella margin", f"£{r.umbrella_margin_paid:,.0f}")
s4.metric("Your pension", f"£{r.employee_pension_contribution:,.0f}")
s5.metric("Employer pension", f"£{r.employer_pension_contribution:,.0f}")

st.markdown("---")
st.caption(
    "Figures are indicative only. Tax rates and thresholds based on 2024/25 HMRC published rates. "
    "Not financial advice — verify with your accountant."
)
