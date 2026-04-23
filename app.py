"""
Rate Calculator — Ltd Co, Umbrella, Salaried.
Tax year selector drives rates across all three tabs.
"""

import streamlit as st
from calculator import calculate as umbrella_calculate, UmbrellaAssumptions
from salaried_calculator import calculate as salaried_calculate, SalariedAssumptions
from ltd_co_calculator import calculate as ltd_co_calculate, LtdCoAssumptions
from tax_years import TAX_YEARS, TAX_YEAR_OPTIONS, DEFAULT_TAX_YEAR

st.set_page_config(
    page_title="Rate Calculator",
    page_icon="🧮",
    layout="wide",
)

st.title("🧮 Rate Calculator")

# ── Tax year selector — global, above tabs ────────────────────────────────────
col_yr, col_gap = st.columns([1, 2])
with col_yr:
    selected_year = st.selectbox(
        "Tax year",
        TAX_YEAR_OPTIONS,
        index=TAX_YEAR_OPTIONS.index(DEFAULT_TAX_YEAR),
        help="Rates and thresholds update across all three calculators when you change tax year.",
    )

ty = TAX_YEARS[selected_year]

def ty_note(key):
    note = ty.get("notes", {}).get(key)
    if note:
        st.caption(f"ℹ️ {note}")

st.caption(f"UK contracting & employment — {selected_year}")
st.markdown("---")

tab_ltd, tab_umbrella, tab_salaried = st.tabs(["Ltd Co (Outside IR35)", "Umbrella (Inside IR35)", "Full-Time Salaried"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB — LTD CO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_ltd:
    st.subheader("Ltd Co Rate Calculator")
    st.caption("Outside IR35 — invoicing via your own limited company or through agency (amount is post agency deduction). Salary + dividends extraction.")

    col_input, col_gap = st.columns([1, 2])
    with col_input:
        l_day_rate = st.number_input(
            "Day Rate (£/day)",
            min_value=100, max_value=2_000, value=440, step=25,
            help="The rate your Ltd Co invoices / receives from the client or agency.",
            key="l_day_rate",
        )

    with st.expander("Assumptions — click to edit"):
        st.markdown("**Working pattern**")
        c1, c2, c3 = st.columns(3)
        with c1:
            l_days_per_week = st.number_input("Days/week", value=5.0, step=0.5, key="l_dpw")
        with c2:
            l_weeks_per_year = st.number_input("Weeks/year", value=46, step=1, key="l_wpy",
                help="Assume 11 days bank holiday and 19 further days off (annual leave).")
        with c3:
            l_hours_per_day = st.number_input("Hours/day", value=7.5, step=0.5, key="l_hpd")

        st.markdown("**Director salary & tax**")
        c1, c2, c3 = st.columns(3)
        with c1:
            l_director_salary = st.number_input(
                "Director salary (£/yr)", value=float(ty["personal_allowance"]), step=100.0, key="l_salary",
                help="Set at personal allowance by default — no income tax and minimal employer NI.",
            )
            ty_note("personal_allowance")
        with c2:
            l_corp_tax = st.number_input(
                "Corporation tax rate (%)", value=ty["corporation_tax_rate"] * 100,
                step=1.0, format="%.1f", key="l_corp_tax",
                help="Main rate 25% on profits ≥ £250k. Small profits relief applies below £50k.",
            ) / 100
        with c3:
            l_div_allowance = st.number_input(
                "Dividend allowance (£/yr)", value=float(ty["dividend_allowance"]),
                step=100.0, key="l_div_allowance",
                help="Tax-free dividend allowance for this tax year.",
            )
            ty_note("dividend_allowance")

        st.markdown("**Employer NI**")
        c1, c2, c3 = st.columns(3)
        with c1:
            l_er_ni_rate = st.number_input(
                "Employer NI rate (%)", value=ty["employer_ni_rate"] * 100,
                step=0.1, format="%.1f", key="l_er_ni_rate",
            ) / 100
            ty_note("employer_ni_rate")
        with c2:
            l_er_ni_threshold = st.number_input(
                "Employer NI secondary threshold (£/yr)",
                value=float(ty["employer_ni_threshold"]),
                step=100.0, key="l_er_ni_threshold",
            )
            ty_note("employer_ni_threshold")

        st.markdown("**Business expenses**")
        c1, c2, c3 = st.columns(3)
        with c1:
            l_pi = st.number_input(
                "Professional indemnity insurance (£/yr)", value=1_200, step=100, key="l_pi",
                help="PI insurance is a standard contractor cost. Deducted before corporation tax.",
            )
        with c2:
            l_life = st.number_input(
                "Relevant Life insurance (£/yr)", value=864, step=50, key="l_life",
                help="Company-paid life insurance. Tax-efficient — premiums paid before profit.",
            )
        with c3:
            l_ci = st.number_input(
                "Critical illness / IP insurance (£/yr)", value=600, step=50, key="l_ci",
                help="Your contractor equivalent of employer sick pay. Deducted before corporation tax.",
            )

        c1, c2, c3 = st.columns(3)
        with c1:
            l_accountancy = st.number_input("Accountancy (£/yr)", value=1_800, step=100, key="l_accountancy")
        with c2:
            l_other = st.number_input(
                "Other business expenses (£/yr)", value=1_000, step=100, key="l_other",
                help="Phone, software, insurance, home office etc.",
            )

        st.markdown("**Pension**")
        c1, c2, c3 = st.columns(3)
        with c1:
            l_pension = st.number_input(
                "Employer pension (£/yr)", value=6_000, step=100, key="l_pension",
                help="Company pension contribution. Deducted before corporation tax.",
            )

    la = LtdCoAssumptions(
        days_per_week=l_days_per_week,
        weeks_per_year=l_weeks_per_year,
        hours_per_day=l_hours_per_day,
        director_salary=l_director_salary,
        employer_ni_secondary_threshold=l_er_ni_threshold,
        employer_ni_rate=l_er_ni_rate,
        corporation_tax_rate=l_corp_tax,
        dividend_allowance=l_div_allowance,
        dividend_basic_rate=ty["dividend_basic_rate"],
        dividend_higher_rate=ty["dividend_higher_rate"],
        basic_rate_band_upper=ty["basic_rate_ceiling"],
        personal_allowance=ty["personal_allowance"],
        professional_indemnity_per_year=l_pi,
        employer_pension_per_month=l_pension / 12,
        relevant_life_insurance_per_month=l_life / 12,
        critical_illness_per_month=l_ci / 12,
        accountancy_per_year=l_accountancy,
        other_expenses_per_year=l_other,
    )
    lr = ltd_co_calculate(l_day_rate, la)

    st.markdown("---")
    st.subheader("Net Take-Home")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Annual", f"£{lr.annual_net:,.0f}")
    m2.metric("Monthly", f"£{lr.monthly_net:,.0f}")
    m3.metric("Daily equivalent", f"£{lr.daily_net:,.2f}")
    m4.metric("Effective tax rate", f"{lr.effective_tax_rate:.1%}")

    with st.expander("Full Breakdown"):
        left, right = st.columns(2)
        with left:
            st.markdown("**Step 1 — Company-level deductions**")
            for label, value, is_deduction in [
                ("Gross contract income", lr.annual_gross_contract_income, False),
                ("Less: Director salary", -lr.director_salary, True),
                ("Less: Employer NI on salary", -lr.employer_ni_on_salary, True),
                ("Less: Professional indemnity insurance", -lr.professional_indemnity_annual, True),
                ("Less: Relevant Life insurance", -lr.relevant_life_insurance_annual, True),
                ("Less: Critical illness / IP insurance", -lr.critical_illness_annual, True),
                ("Less: Accountancy fees", -lr.accountancy_annual, True),
                ("Less: Other business expenses", -lr.other_expenses_annual, True),
                ("Less: Employer pension", -lr.employer_pension_annual, True),
                ("= Taxable profit", lr.taxable_profit, False),
                ("Less: Corporation tax", -lr.corporation_tax, True),
                ("= Distributable profit", lr.distributable_profit, False),
            ]:
                ca, cb = st.columns([3, 1])
                style = "color: #cc0000;" if is_deduction else "font-weight: bold;"
                ca.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
                cb.markdown(f"<span style='{style}'>£{value:,.2f}</span>", unsafe_allow_html=True)

        with right:
            st.markdown("**Step 2 — Personal income**")
            for label, value in [
                ("Director salary received", lr.director_salary),
                ("Dividends drawn", lr.dividends_drawn),
                ("Total personal income", lr.total_personal_income),
            ]:
                ca, cb = st.columns([3, 1])
                bold = "font-weight: bold;" if "Total" in label else ""
                ca.markdown(f"<span style='{bold}'>{label}</span>", unsafe_allow_html=True)
                cb.markdown(f"<span style='{bold}'>£{value:,.2f}</span>", unsafe_allow_html=True)

            st.markdown("")
            st.markdown("**Step 3 — Personal tax on dividends**")
            for label, value, is_deduction in [
                ("Dividend allowance — tax free", lr.dividend_allowance_tax_free, False),
                ("Dividends within basic rate band", lr.dividends_basic_rate_band, False),
                ("Dividends above basic rate band", lr.dividends_higher_rate_band, False),
                ("Less: Dividend tax", -lr.dividend_tax, True),
                ("Net dividends after personal tax", lr.net_dividends_after_tax, False),
                ("= Net take-home (annual)", lr.annual_net, False),
            ]:
                ca, cb = st.columns([3, 1])
                style = "color: #cc0000;" if is_deduction else ("font-weight: bold;" if "take-home" in label else "")
                ca.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
                cb.markdown(f"<span style='{style}'>£{value:,.2f}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Tax & Deductions Summary")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Corporation tax", f"£{lr.corporation_tax_paid:,.0f}")
    s2.metric("Dividend tax", f"£{lr.dividend_tax_paid:,.0f}")
    s3.metric("Employer NI", f"£{lr.employer_ni_paid:,.0f}")
    s4.metric("Pension (company)", f"£{lr.total_pension:,.0f}")
    s5.metric("Critical illness (after-tax cost)", f"£{lr.critical_illness_after_tax_cost:,.0f}")

    with st.expander("Contractor Protection & Context"):
        for label, value in [
            ("Critical illness / IP insurance (gross)", lr.critical_illness_annual),
            ("After-tax cost to company", lr.critical_illness_after_tax_cost),
            ("Gross contract income", lr.annual_gross_contract_income),
            ("Total pension (employer contribution)", lr.total_pension),
        ]:
            ca, cb = st.columns([3, 1])
            bold = "font-weight: bold;" if "Total" in label or "Gross contract" in label else ""
            ca.markdown(f"<span style='{bold}'>{label}</span>", unsafe_allow_html=True)
            cb.markdown(f"<span style='{bold}'>£{value:,.2f}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Figures are indicative only. Tax rates based on published HMRC rates. Not financial advice.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB — UMBRELLA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_umbrella:
    st.subheader("Umbrella Rate Calculator")
    st.caption("Agency day rate processed via an umbrella company — Inside IR35.")

    col_input, col_gap = st.columns([1, 2])
    with col_input:
        u_day_rate = st.number_input(
            "Day Rate (£/day)",
            min_value=100, max_value=2_000, value=550, step=25,
            help="The rate you invoice via the agency / umbrella.",
            key="u_day_rate",
        )

    with st.expander("Assumptions — click to edit"):
        st.markdown("**Working pattern**")
        c1, c2, c3 = st.columns(3)
        with c1:
            u_days_per_week = st.number_input("Days/week", value=5.0, step=0.5, key="u_dpw")
        with c2:
            u_weeks_per_year = st.number_input("Weeks/year", value=46, step=1, key="u_wpy",
                help="Assume 11 days bank holiday and 19 further days off (annual leave).")
        with c3:
            u_hours_per_day = st.number_input("Hours/day", value=7.5, step=0.5, key="u_hpd")

        st.markdown("**Umbrella costs**")
        c1, c2, c3 = st.columns(3)
        with c1:
            u_margin_annual = st.number_input("Umbrella margin (£/yr)", value=1_150, step=50, key="u_margin",
                help="Annual umbrella fee. Typical £15–£30/week — default is £25 × 46 weeks.")
        with c2:
            u_levy_rate = st.number_input("Apprenticeship Levy rate (%)", value=0.5, step=0.1,
                format="%.1f", key="u_levy",
                help="0.5% of payroll. Most umbrellas pass this through. Set to 0 if not charged.") / 100

        st.markdown("**Employer NI**")
        c1, c2, c3 = st.columns(3)
        with c1:
            u_er_ni_rate = st.number_input(
                "Employer NI rate (%)", value=ty["employer_ni_rate"] * 100,
                step=0.1, format="%.1f", key="u_er_ni_rate",
            ) / 100
            ty_note("employer_ni_rate")
        with c2:
            u_er_ni_threshold = st.number_input(
                "Employer NI secondary threshold (£/yr)",
                value=float(ty["employer_ni_threshold"]),
                step=100.0, key="u_er_ni_threshold",
            )
            ty_note("employer_ni_threshold")

        st.markdown("**Pension**")
        c1, c2, c3 = st.columns(3)
        with c1:
            u_pension_type = st.selectbox(
                "Pension scheme type",
                ["Net pay arrangement", "Relief at source", "Salary sacrifice"],
                key="u_pension_type",
            )
        with c2:
            u_ee_pension = st.number_input("Employee contribution (%)", value=5.0, step=0.5,
                format="%.1f", key="u_ee_pension") / 100
        with c3:
            u_er_pension = st.number_input("Employer contribution (%)", value=3.0, step=0.5,
                format="%.1f", key="u_er_pension") / 100

        u_ni_passback = False
        if u_pension_type == "Salary sacrifice":
            u_ni_passback = st.checkbox("Employer passes NI saving to pension?", value=False, key="u_ni_passback")

    ua = UmbrellaAssumptions(
        days_per_week=u_days_per_week,
        weeks_per_year=u_weeks_per_year,
        hours_per_day=u_hours_per_day,
        personal_allowance=ty["personal_allowance"],
        basic_rate_ceiling=ty["basic_rate_ceiling"],
        higher_rate_ceiling=ty["higher_rate_ceiling"],
        income_tax_basic=ty["income_tax_basic"],
        income_tax_higher=ty["income_tax_higher"],
        income_tax_additional=ty["income_tax_additional"],
        ni_primary_threshold=ty["ni_primary_threshold"],
        ni_rate_standard=ty["ni_rate_standard"],
        ni_upper_earnings_limit=ty["ni_upper_earnings_limit"],
        ni_rate_above_uel=ty["ni_rate_above_uel"],
        umbrella_margin_per_week=u_margin_annual / u_weeks_per_year,
        employer_ni_secondary_threshold=u_er_ni_threshold,
        employer_ni_rate=u_er_ni_rate,
        apprenticeship_levy_rate=u_levy_rate,
        pension_scheme_type=u_pension_type,
        employee_pension_rate=u_ee_pension,
        employer_pension_rate=u_er_pension,
        employer_passes_ni_saving_to_pension=u_ni_passback,
    )
    ur = umbrella_calculate(u_day_rate, ua)

    st.markdown("---")
    st.subheader("Net Take-Home")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Annual", f"£{ur.annual_net:,.0f}")
    m2.metric("Monthly", f"£{ur.monthly_net:,.0f}")
    m3.metric("Daily equivalent", f"£{ur.daily_net:,.2f}")
    m4.metric("Effective tax rate", f"{ur.effective_tax_rate:.1%}")

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

    st.markdown("---")
    st.subheader("Tax & Deductions Summary")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Income tax", f"£{ur.income_tax_paid:,.0f}")
    s2.metric("Employee NI", f"£{ur.employee_ni_paid:,.0f}")
    s3.metric("Umbrella margin", f"£{ur.umbrella_margin_paid:,.0f}")
    s4.metric("Your pension", f"£{ur.employee_pension_contribution:,.0f}")
    s5.metric("Employer pension", f"£{ur.employer_pension_contribution:,.0f}")

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
    st.caption("Figures are indicative only. Tax rates based on published HMRC rates. Not financial advice.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB — SALARIED
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_salaried:
    st.subheader("Full-Time Salaried Calculator")
    st.caption("Direct employment — PAYE. Income tax and NI deducted at source.")

    col_input, col_gap = st.columns([1, 2])
    with col_input:
        s_salary = st.number_input(
            "Annual Salary (£/yr)",
            min_value=10_000, max_value=500_000, value=98_500, step=500,
            help="Your gross contracted salary before any deductions.",
            key="s_salary",
        )

    with st.expander("Assumptions — click to edit"):
        st.markdown("**Working pattern**")
        c1, c2, c3 = st.columns(3)
        with c1:
            s_days_per_week = st.number_input("Days/week", value=5.0, step=0.5, key="s_dpw")
        with c2:
            s_weeks_per_year = st.number_input("Weeks/year", value=46, step=1, key="s_wpy",
                help="Assume 11 days bank holiday and 19 further days off (annual leave).")
        with c3:
            s_hours_per_day = st.number_input("Hours/day", value=7.5, step=0.5, key="s_hpd")

        st.markdown("**Employer NI**")
        c1, c2, c3 = st.columns(3)
        with c1:
            s_er_ni_rate = st.number_input(
                "Employer NI rate (%)", value=ty["employer_ni_rate"] * 100,
                step=0.1, format="%.1f", key="s_er_ni_rate",
            ) / 100
            ty_note("employer_ni_rate")
        with c2:
            s_er_ni_threshold = st.number_input(
                "Employer NI secondary threshold (£/yr)",
                value=float(ty["employer_ni_threshold"]),
                step=100.0, key="s_er_ni_threshold",
            )
            ty_note("employer_ni_threshold")

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
            s_ee_pension = st.number_input("Employee contribution (%)", value=13.5, step=0.5,
                format="%.1f", key="s_ee_pension") / 100
        with c3:
            s_er_pension = st.number_input("Employer contribution (%)", value=28.97, step=0.5,
                format="%.2f", key="s_er_pension") / 100

        s_ni_passback = False
        if s_pension_type == "Salary sacrifice":
            s_ni_passback = st.checkbox("Employer passes NI saving to pension?", value=False, key="s_ni_passback")

        st.markdown("**Other employer costs**")
        c1, c2, c3 = st.columns(3)
        with c1:
            s_sick_pay = st.number_input(
                "Employer sick pay liability (% of salary)", value=2.0, step=0.5,
                format="%.1f", key="s_sick_pay",
                help="2% ≈ 5 days full pay per year.",
            ) / 100

    sa = SalariedAssumptions(
        days_per_week=s_days_per_week,
        weeks_per_year=s_weeks_per_year,
        hours_per_day=s_hours_per_day,
        personal_allowance=ty["personal_allowance"],
        basic_rate_ceiling=ty["basic_rate_ceiling"],
        higher_rate_ceiling=ty["higher_rate_ceiling"],
        income_tax_basic=ty["income_tax_basic"],
        income_tax_higher=ty["income_tax_higher"],
        income_tax_additional=ty["income_tax_additional"],
        ni_primary_threshold=ty["ni_primary_threshold"],
        ni_rate_standard=ty["ni_rate_standard"],
        ni_upper_earnings_limit=ty["ni_upper_earnings_limit"],
        ni_rate_above_uel=ty["ni_rate_above_uel"],
        employer_ni_secondary_threshold=s_er_ni_threshold,
        employer_ni_rate=s_er_ni_rate,
        pension_scheme_type=s_pension_type,
        employee_pension_rate=s_ee_pension,
        employer_pension_rate=s_er_pension,
        employer_passes_ni_saving_to_pension=s_ni_passback,
        employer_sick_pay_rate=s_sick_pay,
    )
    sr = salaried_calculate(s_salary, sa)

    st.markdown("---")
    st.subheader("Net Take-Home")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Annual", f"£{sr.annual_net:,.0f}")
    m2.metric("Monthly", f"£{sr.monthly_net:,.0f}")
    m3.metric("Daily equivalent", f"£{sr.daily_net:,.2f}")
    m4.metric("Effective tax rate", f"{sr.effective_tax_rate:.1%}")

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

    st.markdown("---")
    st.subheader("Tax & Deductions Summary")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Income tax", f"£{sr.income_tax_paid:,.0f}")
    s2.metric("Employee NI", f"£{sr.employee_ni_paid:,.0f}")
    s3.metric("Your pension", f"£{sr.employee_pension_contribution:,.0f}")
    s4.metric("Employer pension", f"£{sr.employer_pension_contribution:,.0f}")
    s5.metric("Employer NI", f"£{sr.employer_ni:,.0f}")

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
    st.caption("Figures are indicative only. Tax rates based on published HMRC rates. Not financial advice.")
