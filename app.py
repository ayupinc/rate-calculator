"""
Rate Calculator — Umbrella, Salaried, Ltd Co (coming soon).
2024/25 tax year.
"""

import streamlit as st
from calculator import calculate as umbrella_calculate, UmbrellaAssumptions
from salaried_calculator import calculate as salaried_calculate, SalariedAssumptions

st.set_page_config(
    page_title="Rate Calculator",
    page_icon="🧮",
    layout="wide",
)

st.title("🧮 Rate Calculator")
st.caption("2024/25 tax year — UK contracting & employment")

tab1, tab2, tab3 = st.tabs(["Umbrella (Inside IR35)", "Full-Time Salaried", "Ltd Co (Outside IR35)"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1 — UMBRELLA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    st.subheader("Umbrella Rate Calculator")
    st.caption("Agency day rate processed via an umbrella company — Inside IR35.")

    # Input
    col_input, col_gap = st.columns([1, 2])
    with col_input:
        u_day_rate = st.number_input(
            "Day Rate (£/day)",
            min_value=100, max_value=2_000, value=550, step=25,
            help="The rate you invoice via the agency / umbrella.",
            key="u_day_rate",
        )

    # Assumptions
    with st.expander("Assumptions — click to edit"):
        st.markdown("**Working pattern**")
        c1, c2, c3 = st.columns(3)
        with c1:
            u_days_per_week = st.number_input("Days/week", value=5.0, step=0.5, key="u_dpw")
        with c2:
            u_weeks_per_year = st.number_input("Weeks/year", value=46, step=1, key="u_wpy")
        with c3:
            u_hours_per_day = st.number_input("Hours/day", value=7.5, step=0.5, key="u_hpd")

        st.markdown("**Umbrella costs**")
        c1, c2, c3 = st.columns(3)
        with c1:
            u_margin = st.number_input("Umbrella margin (£/week)", value=25, step=5, key="u_margin")
        with c2:
            u_levy = st.checkbox("Apprenticeship Levy charged?", value=True, key="u_levy")

        st.markdown("**Pension**")
        c1, c2, c3 = st.columns(3)
        with c1:
            u_pension_type = st.selectbox(
                "Pension scheme type",
                ["Net pay arrangement", "Relief at source", "Salary sacrifice"],
                key="u_pension_type",
            )
        with c2:
            u_ee_pension = st.number_input("Employee contribution (%)", value=5.0, step=0.5, format="%.1f", key="u_ee_pension") / 100
        with c3:
            u_er_pension = st.number_input("Employer contribution (%)", value=3.0, step=0.5, format="%.1f", key="u_er_pension") / 100

        u_ni_passback = False
        if u_pension_type == "Salary sacrifice":
            u_ni_passback = st.checkbox("Employer passes NI saving to pension?", value=False, key="u_ni_passback")

    # Calculate
    ua = UmbrellaAssumptions(
        days_per_week=u_days_per_week,
        weeks_per_year=u_weeks_per_year,
        hours_per_day=u_hours_per_day,
        umbrella_margin_per_week=u_margin,
        apprenticeship_levy_rate=0.005 if u_levy else 0.0,
        pension_scheme_type=u_pension_type,
        employee_pension_rate=u_ee_pension,
        employer_pension_rate=u_er_pension,
        employer_passes_ni_saving_to_pension=u_ni_passback,
    )
    ur = umbrella_calculate(u_day_rate, ua)

    # Net take-home
    st.markdown("---")
    st.subheader("Net Take-Home")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Annual", f"£{ur.annual_net:,.0f}")
    m2.metric("Monthly", f"£{ur.monthly_net:,.0f}")
    m3.metric("Daily equivalent", f"£{ur.daily_net:,.2f}")
    m4.metric("Effective tax rate", f"{ur.effective_tax_rate:.1%}")

    # Full breakdown
    with st.expander("Full Breakdown"):
        left, right = st.columns(2)

        with left:
            st.markdown("**Step 1 — Umbrella deductions**")
            for label, value, is_deduction in [
                ("Gross contract income", ur.annual_gross_contract_income, False),
                ("Less: Umbrella margin", -ur.umbrella_margin_annual, True),
                ("Less: Employer NI", -ur.employer_ni, True),
                ("Less: Apprenticeship Levy", -ur.apprenticeship_levy, True),
                ("= Gross PAYE salary", ur.gross_paye_salary, False),
            ]:
                ca, cb = st.columns([3, 1])
                style = "color: #cc0000;" if is_deduction else "font-weight: bold;"
                ca.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
                cb.markdown(f"<span style='{style}'>£{value:,.2f}</span>", unsafe_allow_html=True)

            st.markdown("")
            st.markdown("**Step 2 — Pre-tax deductions**")
            for label, value, is_deduction in [
                ("Gross PAYE salary", ur.gross_paye_salary, False),
                ("Less: Employee pension (pre-tax)", -ur.employee_pension_pretax, True),
                ("= Gross taxable pay", ur.gross_taxable_pay, False),
            ]:
                ca, cb = st.columns([3, 1])
                style = "color: #cc0000;" if is_deduction else "font-weight: bold;"
                ca.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
                cb.markdown(f"<span style='{style}'>£{value:,.2f}</span>", unsafe_allow_html=True)

        with right:
            st.markdown("**Step 3 — Income tax & NI**")
            for label, value, is_deduction in [
                ("Gross taxable pay", ur.gross_taxable_pay, False),
                ("Less: Income tax (basic rate)", -ur.income_tax_basic, True),
                ("Less: Income tax (higher rate)", -ur.income_tax_higher, True),
                ("Less: Income tax (additional rate)", -ur.income_tax_additional, True),
                ("Less: Employee NI (standard)", -ur.employee_ni_standard, True),
                ("Less: Employee NI (above UEL)", -ur.employee_ni_above_uel, True),
                ("Less: Employee pension (post-tax)", -ur.employee_pension_posttax, True),
                ("= Net take-home (annual)", ur.annual_net, False),
            ]:
                ca, cb = st.columns([3, 1])
                style = "color: #cc0000;" if is_deduction else "font-weight: bold;"
                ca.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
                cb.markdown(f"<span style='{style}'>£{value:,.2f}</span>", unsafe_allow_html=True)

    # Tax summary
    st.markdown("---")
    st.subheader("Tax & Deductions Summary")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Income tax", f"£{ur.income_tax_paid:,.0f}")
    s2.metric("Employee NI", f"£{ur.employee_ni_paid:,.0f}")
    s3.metric("Umbrella margin", f"£{ur.umbrella_margin_paid:,.0f}")
    s4.metric("Your pension", f"£{ur.employee_pension_contribution:,.0f}")
    s5.metric("Employer pension", f"£{ur.employer_pension_contribution:,.0f}")

    # Cost to client
    with st.expander("Cost to Client"):
        for label, value in [
            ("Gross contract fee", ur.annual_gross_contract_income),
            ("  Of which: umbrella margin", ur.umbrella_margin_annual),
            ("  Of which: employer NI", ur.employer_ni),
            ("  Of which: apprenticeship levy", ur.apprenticeship_levy),
            ("  Of which: employer pension", ur.employer_pension_annual),
            ("Total cost to client", ur.total_cost_to_client),
            ("Your gross PAYE salary as % of client cost", None),
        ]:
            ca, cb = st.columns([3, 1])
            bold = "font-weight: bold;" if "Total" in label or label == "Gross contract fee" else ""
            ca.markdown(f"<span style='{bold}'>{label}</span>", unsafe_allow_html=True)
            if value is not None:
                cb.markdown(f"<span style='{bold}'>£{value:,.2f}</span>", unsafe_allow_html=True)
            else:
                cb.markdown(f"<span style='{bold}'>{ur.gross_salary_pct_of_client_cost:.1%}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Figures are indicative only. Tax rates based on 2024/25 HMRC published rates. Not financial advice.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2 — SALARIED
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    st.subheader("Full-Time Salaried Calculator")
    st.caption("Direct employment — PAYE. Income tax and NI deducted at source.")

    # Input
    col_input, col_gap = st.columns([1, 2])
    with col_input:
        s_salary = st.number_input(
            "Annual Salary (£/yr)",
            min_value=10_000, max_value=500_000, value=98_500, step=500,
            help="Your gross contracted salary before any deductions.",
            key="s_salary",
        )

    # Assumptions
    with st.expander("Assumptions — click to edit"):
        st.markdown("**Working pattern**")
        c1, c2, c3 = st.columns(3)
        with c1:
            s_days_per_week = st.number_input("Days/week", value=5.0, step=0.5, key="s_dpw")
        with c2:
            s_weeks_per_year = st.number_input("Weeks/year", value=46, step=1, key="s_wpy")
        with c3:
            s_hours_per_day = st.number_input("Hours/day", value=7.5, step=0.5, key="s_hpd")

        st.markdown("**Pension**")
        c1, c2, c3 = st.columns(3)
        with c1:
            s_pension_type = st.selectbox(
                "Pension scheme type",
                ["Relief at source", "Net pay arrangement", "Salary sacrifice"],
                key="s_pension_type",
                help="Relief at source: pension deducted after tax, HMRC tops up at 20%. Net pay: deducted before tax and NI. Salary sacrifice: gross salary reduced, saves employee and employer NI.",
            )
        with c2:
            s_ee_pension = st.number_input("Employee contribution (%)", value=13.5, step=0.5, format="%.1f", key="s_ee_pension") / 100
        with c3:
            s_er_pension = st.number_input("Employer contribution (%)", value=28.97, step=0.5, format="%.2f", key="s_er_pension") / 100

        s_ni_passback = False
        if s_pension_type == "Salary sacrifice":
            s_ni_passback = st.checkbox("Employer passes NI saving to pension?", value=False, key="s_ni_passback")

        st.markdown("**Other employer costs**")
        c1, c2, c3 = st.columns(3)
        with c1:
            s_sick_pay = st.number_input(
                "Employer sick pay liability (% of salary)", value=2.0, step=0.5, format="%.1f", key="s_sick_pay",
                help="2% ≈ 5 days full pay per year.",
            ) / 100

    # Calculate
    sa = SalariedAssumptions(
        days_per_week=s_days_per_week,
        weeks_per_year=s_weeks_per_year,
        hours_per_day=s_hours_per_day,
        pension_scheme_type=s_pension_type,
        employee_pension_rate=s_ee_pension,
        employer_pension_rate=s_er_pension,
        employer_passes_ni_saving_to_pension=s_ni_passback,
        employer_sick_pay_rate=s_sick_pay,
    )
    sr = salaried_calculate(s_salary, sa)

    # Net take-home
    st.markdown("---")
    st.subheader("Net Take-Home")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Annual", f"£{sr.annual_net:,.0f}")
    m2.metric("Monthly", f"£{sr.monthly_net:,.0f}")
    m3.metric("Daily equivalent", f"£{sr.daily_net:,.2f}")
    m4.metric("Effective tax rate", f"{sr.effective_tax_rate:.1%}")

    # Full breakdown
    with st.expander("Full Breakdown"):
        left, right = st.columns(2)

        with left:
            st.markdown("**Step 1 — Gross salary**")
            for label, value in [
                ("Gross annual salary", s_salary),
                ("Equivalent day rate", sr.equivalent_day_rate),
            ]:
                ca, cb = st.columns([3, 1])
                ca.markdown(f"<span style='font-weight: bold;'>{label}</span>", unsafe_allow_html=True)
                cb.markdown(f"<span style='font-weight: bold;'>£{value:,.2f}</span>", unsafe_allow_html=True)

            st.markdown("")
            st.markdown("**Step 2 — Pre-tax deductions**")
            for label, value, is_deduction in [
                ("Gross salary", s_salary, False),
                ("Less: Employee pension (pre-tax)", -sr.employee_pension_pretax, True),
                ("= Gross taxable pay", sr.gross_taxable_pay, False),
            ]:
                ca, cb = st.columns([3, 1])
                style = "color: #cc0000;" if is_deduction else "font-weight: bold;"
                ca.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
                cb.markdown(f"<span style='{style}'>£{value:,.2f}</span>", unsafe_allow_html=True)

            st.markdown("")
            st.markdown("**Step 3 — Income tax & NI**")
            for label, value, is_deduction in [
                ("Gross taxable pay", sr.gross_taxable_pay, False),
                ("Less: Income tax (basic rate)", -sr.income_tax_basic, True),
                ("Less: Income tax (higher rate)", -sr.income_tax_higher, True),
                ("Less: Income tax (additional rate)", -sr.income_tax_additional, True),
                ("Less: Employee NI (standard)", -sr.employee_ni_standard, True),
                ("Less: Employee NI (above UEL)", -sr.employee_ni_above_uel, True),
                ("Less: Employee pension (post-tax)", -sr.employee_pension_posttax, True),
                ("= Net take-home (annual)", sr.annual_net, False),
            ]:
                ca, cb = st.columns([3, 1])
                style = "color: #cc0000;" if is_deduction else "font-weight: bold;"
                ca.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
                cb.markdown(f"<span style='{style}'>£{value:,.2f}</span>", unsafe_allow_html=True)

        with right:
            st.markdown("**Pension memo**")
            for label, value in [
                ("Your pension contribution", sr.employee_pension_contribution),
                ("HMRC basic rate top-up", sr.hmrc_basic_rate_topup),
                ("Employer NI saving to pension", sr.employer_ni_saving_to_pension),
                ("Total pension pot funded", sr.total_pension_pot),
            ]:
                ca, cb = st.columns([3, 1])
                bold = "font-weight: bold;" if "Total" in label else ""
                ca.markdown(f"<span style='{bold}'>{label}</span>", unsafe_allow_html=True)
                cb.markdown(f"<span style='{bold}'>£{value:,.2f}</span>", unsafe_allow_html=True)

    # Tax summary
    st.markdown("---")
    st.subheader("Tax & Deductions Summary")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Income tax", f"£{sr.income_tax_paid:,.0f}")
    s2.metric("Employee NI", f"£{sr.employee_ni_paid:,.0f}")
    s3.metric("Your pension", f"£{sr.employee_pension_contribution:,.0f}")
    s4.metric("Employer pension", f"£{sr.employer_pension_contribution:,.0f}")
    s5.metric("Employer NI", f"£{sr.employer_ni:,.0f}")

    # Cost to employer
    with st.expander("Cost to Employer"):
        for label, value in [
            ("Gross salary", s_salary),
            ("  Employer NI", sr.employer_ni),
            ("  Employer pension contribution", sr.employer_pension),
            ("  Employer sick pay liability", sr.employer_sick_pay_liability),
            ("Total cost to employer", sr.total_cost_to_employer),
            ("Breakeven contractor day rate", sr.breakeven_day_rate),
        ]:
            ca, cb = st.columns([3, 1])
            bold = "font-weight: bold;" if "Total" in label or "Breakeven" in label or label == "Gross salary" else ""
            ca.markdown(f"<span style='{bold}'>{label}</span>", unsafe_allow_html=True)
            cb.markdown(f"<span style='{bold}'>£{value:,.2f}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Figures are indicative only. Tax rates based on 2024/25 HMRC published rates. Not financial advice.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3 — LTD CO (COMING SOON)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:
    st.subheader("Ltd Co Calculator")
    st.caption("Outside IR35 — invoicing via your own limited company.")
    st.info("Coming soon. This calculator is under development.")
