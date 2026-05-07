"""
Rate Calculator — Ltd Co, Umbrella, Salaried.
Tax year selector and display period selector drive all three tabs.
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

# ── Global selectors — tax year and display period ────────────────────────────
col_yr, col_period, col_gap = st.columns([1, 1, 1])
with col_yr:
    selected_year = st.selectbox(
        "Tax year",
        TAX_YEAR_OPTIONS,
        index=TAX_YEAR_OPTIONS.index(DEFAULT_TAX_YEAR),
        help="Rates and thresholds update across all three calculators when you change tax year.",
    )
with col_period:
    display_period = st.selectbox(
        "Display figures",
        ["Per Year", "Per Month", "Per Week"],
        index=0,
        help="Changes how output figures are shown. All calculations always run annually so that tax bands and thresholds are applied correctly.",
    )

ty = TAX_YEARS[selected_year]

# ── Helper functions ──────────────────────────────────────────────────────────
def ty_note(key):
    note = ty.get("notes", {}).get(key)
    if note:
        st.caption(f"ℹ️ {note}")

def fmt(value):
    """Convert an annual figure to the selected display period."""
    if display_period == "Per Year":
        return f"£{value:,.2f}"
    elif display_period == "Per Month":
        return f"£{value / 12:,.2f}"
    else:  # Per Week
        return f"£{value / 52:,.2f}"

def mfmt(value):
    """Metric format — no pence for large figures."""
    if display_period == "Per Year":
        return f"£{value:,.0f}"
    elif display_period == "Per Month":
        return f"£{value / 12:,.0f}"
    else:
        return f"£{value / 52:,.2f}"

def plabel(label):
    """Update period references in labels."""
    if display_period == "Per Year":
        return label
    elif display_period == "Per Month":
        return label.replace("(annual)", "(monthly)").replace("annual", "monthly")
    else:
        return label.replace("(annual)", "(weekly)").replace("annual", "weekly")

psuffix = {"Per Year": "/yr", "Per Month": "/mo", "Per Week": "/wk"}[display_period]

st.caption(
    f"UK contracting & employment — {selected_year} — "
    f"figures shown {display_period.lower()}. All calculations run annually."
)
st.markdown("---")

tab_ltd, tab_umbrella, tab_salaried = st.tabs(["Ltd Co (Outside IR35)", "Umbrella (Inside IR35)", "Full-Time Salaried"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB — LTD CO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_ltd:
    st.subheader("Ltd Co Rate Calculator")
    st.caption("Outside IR35 — invoicing via your own limited company or through agency (amount is post agency deduction). Salary + dividends extraction.")

    col_rtype, col_input, col_gap = st.columns([1, 1, 1])
    with col_rtype:
        l_rate_period = st.selectbox(
            "Rate quoted as",
            ["Per Day", "Per Week", "Per Month", "Per Year"],
            index=0, key="l_rate_period",
            help="Select how your rate is quoted. Converted to a daily rate before calculating.",
        )
    with col_input:
        l_rate_labels = {"Per Day": "Day Rate (£/day)", "Per Week": "Weekly Rate (£/week)",
                         "Per Month": "Monthly Rate (£/month)", "Per Year": "Annual Rate (£/year)"}
        l_rate_defaults = {"Per Day": 440.0, "Per Week": 2200.0,
                           "Per Month": 9533.0, "Per Year": 114400.0}
        l_rate_input = st.number_input(
            l_rate_labels[l_rate_period],
            min_value=1.0, max_value=500_000.0,
            value=l_rate_defaults[l_rate_period],
            step=0.50, format="%.2f",
            help="The rate your Ltd Co invoices / receives from the client or agency.",
            key="l_rate_input",
        )

    with st.expander("Assumptions — click to edit"):

        def a_row(label, widget_fn, note=""):
            """Render a three-column assumption row: label | widget | note."""
            ca, cb, cc = st.columns([2, 1, 3])
            ca.markdown(f"<span style='font-size:0.95em;'>{label}</span>", unsafe_allow_html=True)
            with cb:
                result = widget_fn()
            cc.markdown(f"<span style='color:#888888;font-size:0.85em;'>{note}</span>", unsafe_allow_html=True)
            return result

        def a_header(text):
            st.markdown(f"**{text}**")
            ca, cb, cc = st.columns([2, 1, 3])
            ca.markdown("<span style='color:#888;font-size:0.8em;'>Setting</span>", unsafe_allow_html=True)
            cb.markdown("<span style='color:#888;font-size:0.8em;'>Value</span>", unsafe_allow_html=True)
            cc.markdown("<span style='color:#888;font-size:0.8em;'>Note</span>", unsafe_allow_html=True)

        a_header("Working pattern")
        l_days_per_week = a_row("Days per week",
            lambda: st.number_input("", value=5.0, step=0.5, key="l_dpw", label_visibility="collapsed"),
            "Number of days you work per week")
        l_weeks_per_year = a_row("Weeks per year",
            lambda: st.number_input("", value=46, step=1, key="l_wpy", label_visibility="collapsed"),
            "Billable weeks — exclude bank holidays and annual leave. 46 weeks ≈ 6 weeks off.")
        l_hours_per_day = a_row("Hours per day",
            lambda: st.number_input("", value=7.5, step=0.5, key="l_hpd", label_visibility="collapsed"),
            "Used to calculate hourly equivalent rate only")

        st.markdown("")
        a_header("Director salary & tax")
        l_director_salary = a_row("Director salary (£/yr)",
            lambda: st.number_input("", value=float(ty["personal_allowance"]), step=100.0, key=f"l_salary_{selected_year}", label_visibility="collapsed"),
            "Set at personal allowance by default — no income tax and minimal employer NI on the salary itself")
        l_corp_tax = a_row("Corporation tax rate (%)",
            lambda: st.number_input("", value=ty["corporation_tax_rate"] * 100, step=1.0, format="%.1f", key=f"l_corp_tax_{selected_year}", label_visibility="collapsed") / 100,
            "Main rate 25% on profits ≥ £250k. Small profits relief may apply below £50k — check with your accountant")
        l_div_allowance = a_row("Dividend allowance (£/yr)",
            lambda: st.number_input("", value=float(ty["dividend_allowance"]), step=100.0, key=f"l_div_allowance_{selected_year}", label_visibility="collapsed"),
            "Dividends within this allowance are tax-free. Updates with tax year selection.")

        st.markdown("")
        a_header("Employer NI")
        l_er_ni_rate = a_row("Employer NI rate (%)",
            lambda: st.number_input("", value=ty["employer_ni_rate"] * 100, step=0.1, format="%.1f", key=f"l_er_ni_rate_{selected_year}", label_visibility="collapsed") / 100,
            "Rate charged on salary above the secondary threshold. Updates with tax year selection.")
        l_er_ni_threshold = a_row("Secondary threshold (£/yr)",
            lambda: st.number_input("", value=float(ty["employer_ni_threshold"]), step=100.0, key=f"l_er_ni_threshold_{selected_year}", label_visibility="collapsed"),
            "Employer NI is only charged on salary above this amount. Updates with tax year selection.")

        st.markdown("")
        a_header("Business expenses")
        l_pi = a_row("Professional indemnity insurance (£/yr)",
            lambda: st.number_input("", value=1_200, step=100, key="l_pi", label_visibility="collapsed"),
            "Deducted before corporation tax. Typical contractor cost — check your actual premium.")
        l_life = a_row("Relevant Life insurance (£/yr)",
            lambda: st.number_input("", value=864, step=50, key="l_life", label_visibility="collapsed"),
            "Company-paid life cover. Tax-efficient — premiums paid from pre-tax profit.")
        l_ci = a_row("Critical illness / IP insurance (£/yr)",
            lambda: st.number_input("", value=600, step=50, key="l_ci", label_visibility="collapsed"),
            "Income protection if you cannot work. Contractor equivalent of employer sick pay.")
        l_accountancy = a_row("Accountancy fees (£/yr)",
            lambda: st.number_input("", value=1_800, step=100, key="l_accountancy", label_visibility="collapsed"),
            "Deducted before corporation tax. Adjust to your actual accountant's fee.")
        l_other = a_row("Other business expenses (£/yr)",
            lambda: st.number_input("", value=1_000, step=100, key="l_other", label_visibility="collapsed"),
            "Phone, software, home office, travel etc. All deducted before corporation tax.")

        st.markdown("")
        a_header("Pension")
        l_pension = a_row("Employer pension contribution (£/yr)",
            lambda: st.number_input("", value=6_000, step=100, key="l_pension", label_visibility="collapsed"),
            "Company contribution paid directly into your pension. Deducted before corporation tax — one of the most tax-efficient ways to extract value from your Ltd Co.")

    # Convert input rate to daily
    if l_rate_period == "Per Day":
        l_day_rate = l_rate_input
    elif l_rate_period == "Per Week":
        l_day_rate = l_rate_input / l_days_per_week
    elif l_rate_period == "Per Month":
        l_day_rate = l_rate_input / (l_weeks_per_year * l_days_per_week / 12)
    else:  # Per Year
        l_day_rate = l_rate_input / (l_weeks_per_year * l_days_per_week)

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
    m1.metric(f"Net take-home ({psuffix})", mfmt(lr.annual_net))
    m2.metric("Monthly", f"£{lr.monthly_net:,.0f}")
    m3.metric("Daily equivalent", f"£{lr.daily_net:,.2f}")
    m4.metric("Effective tax rate", f"{lr.effective_tax_rate:.1%}")

    with st.expander("Full Breakdown"):

        def bd_row(label, value, note="", is_deduction=False, is_total=False):
            """Render a single three-column breakdown row."""
            ca, cb, cc = st.columns([3, 1, 2])
            if is_total:
                style = "font-weight: bold;"
            elif is_deduction:
                style = "color: #cc0000;"
            else:
                style = ""
            note_style = "color: #888888; font-size: 0.85em;"
            ca.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
            cb.markdown(f"<span style='{style}'>{fmt(value)}</span>", unsafe_allow_html=True)
            cc.markdown(f"<span style='{note_style}'>{note}</span>", unsafe_allow_html=True)

        def bd_header(text):
            st.markdown(f"**{text}**")
            ca, cb, cc = st.columns([3, 1, 2])
            ca.markdown("<span style='color:#888;font-size:0.8em;'>Description</span>", unsafe_allow_html=True)
            cb.markdown("<span style='color:#888;font-size:0.8em;'>Amount</span>", unsafe_allow_html=True)
            cc.markdown("<span style='color:#888;font-size:0.8em;'>Note</span>", unsafe_allow_html=True)

        # ── Step 1 — Company-level deductions ────────────────────────────────
        bd_header("Step 1 — Company-level deductions")
        bd_row("Gross contract income", lr.annual_gross_contract_income,
            f"{la.days_per_week} days × {la.weeks_per_year} weeks × £{lr.day_rate:,.2f}/day",
            is_total=True)
        bd_row("Less: Director salary", -lr.director_salary,
            "Set at personal allowance — no income tax, minimal employer NI",
            is_deduction=True)
        bd_row("Less: Employer NI on salary", -lr.employer_ni_on_salary,
            f"(£{la.director_salary:,.0f} − £{la.employer_ni_secondary_threshold:,.0f}) × {la.employer_ni_rate:.1%}",
            is_deduction=True)
        bd_row("Less: Professional indemnity insurance", -lr.professional_indemnity_annual,
            "From assumptions", is_deduction=True)
        bd_row("Less: Relevant Life insurance", -lr.relevant_life_insurance_annual,
            "From assumptions", is_deduction=True)
        bd_row("Less: Critical illness / IP insurance", -lr.critical_illness_annual,
            "From assumptions", is_deduction=True)
        bd_row("Less: Accountancy fees", -lr.accountancy_annual,
            "From assumptions", is_deduction=True)
        bd_row("Less: Other business expenses", -lr.other_expenses_annual,
            "From assumptions", is_deduction=True)
        bd_row("Less: Employer pension", -lr.employer_pension_annual,
            "From assumptions — deducted before corporation tax",
            is_deduction=True)
        bd_row("= Taxable profit", lr.taxable_profit,
            "Gross income minus all allowable deductions",
            is_total=True)
        bd_row("Less: Corporation tax", -lr.corporation_tax,
            f"£{lr.taxable_profit:,.0f} × {la.corporation_tax_rate:.0%}",
            is_deduction=True)
        bd_row("= Distributable profit", lr.distributable_profit,
            "Available to draw as dividends",
            is_total=True)

        st.markdown("")

        # ── Step 2 — Personal income ──────────────────────────────────────────
        bd_header("Step 2 — Personal income")
        bd_row("Director salary received", lr.director_salary,
            "Paid via payroll — within personal allowance")
        bd_row("Dividends drawn", lr.dividends_drawn,
            "Full distributable profit drawn as dividends")
        bd_row("Total personal income", lr.total_personal_income,
            "Salary + dividends", is_total=True)

        st.markdown("")

        # ── Step 3 — Personal tax on dividends ───────────────────────────────
        bd_header("Step 3 — Personal tax on dividends")
        bd_row("Dividend allowance — tax free", lr.dividend_allowance_tax_free,
            f"£{la.dividend_allowance:,.0f} annual allowance, no tax")
        bd_row("Dividends within basic rate band", lr.dividends_basic_rate_band,
            f"Taxed at {la.dividend_basic_rate:.2%} (basic rate)")
        bd_row("Dividends above basic rate band", lr.dividends_higher_rate_band,
            f"Taxed at {la.dividend_higher_rate:.2%} (higher rate)")
        bd_row("Less: Dividend tax", -lr.dividend_tax,
            f"Basic £{lr.dividends_basic_rate_band * la.dividend_basic_rate:,.0f} + Higher £{lr.dividends_higher_rate_band * la.dividend_higher_rate:,.0f}",
            is_deduction=True)
        bd_row("Net dividends after personal tax", lr.net_dividends_after_tax,
            "Dividends minus dividend tax")
        bd_row("= Net take-home (annual)", lr.annual_net,
            "Salary + net dividends", is_total=True)

    st.markdown("---")
    st.subheader("Tax & Deductions Summary")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Corporation tax", mfmt(lr.corporation_tax_paid))
    s2.metric("Dividend tax", mfmt(lr.dividend_tax_paid))
    s3.metric("Employer NI", mfmt(lr.employer_ni_paid))
    s4.metric("Pension (company)", mfmt(lr.total_pension))
    s5.metric("Critical illness (after-tax cost)", mfmt(lr.critical_illness_after_tax_cost))

    with st.expander("Contractor Protection & Context"):
        for label, value in [
            ("Critical illness / IP insurance (gross)", lr.critical_illness_annual),
            ("After-tax cost to company", lr.critical_illness_after_tax_cost),
            ("Gross contract income", lr.annual_gross_contract_income),
            ("Total pension (employer contribution)", lr.total_pension),
        ]:
            ca, cb = st.columns([3, 1])
            bold = "font-weight: bold;" if "Total" in label or "Gross contract" in label else ""
            ca.markdown(f"<span style='{bold}'>{plabel(label)}</span>", unsafe_allow_html=True)
            cb.markdown(f"<span style='{bold}'>{fmt(value)}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Figures are indicative only. Tax rates based on published HMRC rates. Not financial advice.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB — UMBRELLA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_umbrella:
    st.subheader("Umbrella Rate Calculator")
    st.caption("Agency day rate processed via an umbrella company — Inside IR35.")

    col_rtype, col_input, col_gap = st.columns([1, 1, 1])
    with col_rtype:
        u_rate_period = st.selectbox(
            "Rate quoted as",
            ["Per Day", "Per Week", "Per Month", "Per Year"],
            index=0, key="u_rate_period",
            help="Select how your rate is quoted. Converted to a daily rate before calculating.",
        )
    with col_input:
        u_rate_labels = {"Per Day": "Day Rate (£/day)", "Per Week": "Weekly Rate (£/week)",
                         "Per Month": "Monthly Rate (£/month)", "Per Year": "Annual Rate (£/year)"}
        u_rate_defaults = {"Per Day": 550.0, "Per Week": 2750.0,
                           "Per Month": 11917.0, "Per Year": 143000.0}
        u_rate_input = st.number_input(
            u_rate_labels[u_rate_period],
            min_value=1.0, max_value=500_000.0,
            value=u_rate_defaults[u_rate_period],
            step=0.50, format="%.2f",
            help="The rate you invoice via the agency / umbrella.",
            key="u_rate_input",
        )

    with st.expander("Assumptions — click to edit"):

        def ua_row(label, widget_fn, note=""):
            ca, cb, cc = st.columns([2, 1, 3])
            ca.markdown(f"<span style='font-size:0.95em;'>{label}</span>", unsafe_allow_html=True)
            with cb:
                result = widget_fn()
            cc.markdown(f"<span style='color:#888888;font-size:0.85em;'>{note}</span>", unsafe_allow_html=True)
            return result

        def ua_header(text):
            st.markdown(f"**{text}**")
            ca, cb, cc = st.columns([2, 1, 3])
            ca.markdown("<span style='color:#888;font-size:0.8em;'>Setting</span>", unsafe_allow_html=True)
            cb.markdown("<span style='color:#888;font-size:0.8em;'>Value</span>", unsafe_allow_html=True)
            cc.markdown("<span style='color:#888;font-size:0.8em;'>Note</span>", unsafe_allow_html=True)

        ua_header("Working pattern")
        u_days_per_week = ua_row("Days per week",
            lambda: st.number_input("", value=5.0, step=0.5, key="u_dpw", label_visibility="collapsed"),
            "Number of days you work per week")
        u_weeks_per_year = ua_row("Weeks per year",
            lambda: st.number_input("", value=46, step=1, key="u_wpy", label_visibility="collapsed"),
            "Set to billable weeks only. Exclude holiday and bank holidays. Holiday pay under umbrella does not add income — it is built into the assignment rate and redistributed by the umbrella.")
        u_hours_per_day = ua_row("Hours per day",
            lambda: st.number_input("", value=7.5, step=0.5, key="u_hpd", label_visibility="collapsed"),
            "Used to calculate hourly equivalent rate only")

        st.markdown("")
        ua_header("Umbrella costs")
        u_margin_annual = ua_row("Umbrella margin (£/yr)",
            lambda: st.number_input("", value=1_150, step=50, key="u_margin", label_visibility="collapsed"),
            "Annual umbrella fee deducted from your assignment rate. Typical £15–£30/week. Default is £25 × 46 weeks.")
        u_levy_rate = ua_row("Apprenticeship Levy (%)",
            lambda: st.number_input("", value=0.5, step=0.1, format="%.1f", key="u_levy", label_visibility="collapsed") / 100,
            "0.5% of your gross PAYE salary, passed through by most umbrellas. Set to 0 if your umbrella does not charge this.")

        st.markdown("")
        ua_header("Employer NI")
        u_er_ni_rate = ua_row("Employer NI rate (%)",
            lambda: st.number_input("", value=ty["employer_ni_rate"] * 100, step=0.1, format="%.1f", key=f"u_er_ni_rate_{selected_year}", label_visibility="collapsed") / 100,
            "Under umbrella, employer NI is charged against your assignment rate — not paid by the client on top. Updates with tax year selection.")
        u_er_ni_threshold = ua_row("Secondary threshold (£/yr)",
            lambda: st.number_input("", value=float(ty["employer_ni_threshold"]), step=100.0, key=f"u_er_ni_threshold_{selected_year}", label_visibility="collapsed"),
            "Employer NI is only charged on gross PAYE salary above this amount. Updates with tax year selection.")

        st.markdown("")
        ua_header("Pension")
        u_pension_type = ua_row("Pension scheme type",
            lambda: st.selectbox("", ["Net pay", "Relief at source", "Salary sacrifice"], key="u_pension_type", label_visibility="collapsed"),
            "Net pay: deducted before tax and NI. Relief at source: deducted post-tax, HMRC tops up at 20%. Salary sacrifice: reduces gross salary, saves employee and employer NI.")
        u_ee_pension = ua_row("Employee contribution (%)",
            lambda: st.number_input("", value=5.0, step=0.5, format="%.1f", key="u_ee_pension", label_visibility="collapsed") / 100,
            "Your personal pension contribution as a percentage of qualifying earnings (£6,240–£50,270)")
        u_er_pension = ua_row("Employer contribution (%)",
            lambda: st.number_input("", value=3.0, step=0.5, format="%.1f", key="u_er_pension", label_visibility="collapsed") / 100,
            "Umbrella employer contribution. Statutory minimum is 3%. Deducted from assignment rate in Step 1.")

        u_ni_passback = False
        if u_pension_type == "Salary sacrifice":
            u_ni_passback = ua_row("Employer passes NI saving to pension?",
                lambda: st.checkbox("", value=False, key="u_ni_passback", label_visibility="collapsed"),
                "If yes, the employer NI saving from salary sacrifice is added to your pension pot.")

    # Convert input rate to daily
    if u_rate_period == "Per Day":
        u_day_rate = u_rate_input
    elif u_rate_period == "Per Week":
        u_day_rate = u_rate_input / u_days_per_week
    elif u_rate_period == "Per Month":
        u_day_rate = u_rate_input / (u_weeks_per_year * u_days_per_week / 12)
    else:  # Per Year
        u_day_rate = u_rate_input / (u_weeks_per_year * u_days_per_week)

    u_pension_type_full = {"Net pay": "Net pay arrangement"}.get(u_pension_type, u_pension_type)
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
        pension_scheme_type=u_pension_type_full,
        employee_pension_rate=u_ee_pension,
        employer_pension_rate=u_er_pension,
        employer_passes_ni_saving_to_pension=u_ni_passback,
    )
    ur = umbrella_calculate(u_day_rate, ua)

    # Derived rate equivalents for the gross PAYE salary breakdown note
    u_gross_paye_daily = ur.gross_paye_salary / ur.days_per_year
    u_gross_paye_weekly = ur.gross_paye_salary / 52
    u_gross_paye_monthly = ur.gross_paye_salary / 12

    st.markdown("---")
    st.subheader("Net Take-Home")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"Net take-home ({psuffix})", mfmt(ur.annual_net))
    m2.metric("Monthly", f"£{ur.monthly_net:,.0f}")
    m3.metric("Daily equivalent", f"£{ur.daily_net:,.2f}")
    m4.metric("Effective tax rate", f"{ur.effective_tax_rate:.1%}")

    with st.expander("Full Breakdown"):

        def ubd_row(label, value, note="", is_deduction=False, is_total=False):
            ca, cb, cc = st.columns([3, 1, 3])
            if is_total:
                style = "font-weight: bold;"
            elif is_deduction:
                style = "color: #cc0000;"
            else:
                style = ""
            note_style = "color: #888888; font-size: 0.85em;"
            ca.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
            cb.markdown(f"<span style='{style}'>{fmt(value)}</span>", unsafe_allow_html=True)
            cc.markdown(f"<span style='{note_style}'>{note}</span>", unsafe_allow_html=True)

        def ubd_header(text):
            st.markdown(f"**{text}**")
            ca, cb, cc = st.columns([3, 1, 3])
            ca.markdown("<span style='color:#888;font-size:0.8em;'>Description</span>", unsafe_allow_html=True)
            cb.markdown("<span style='color:#888;font-size:0.8em;'>Amount</span>", unsafe_allow_html=True)
            cc.markdown("<span style='color:#888;font-size:0.8em;'>Note</span>", unsafe_allow_html=True)

        ubd_header("Step 1 — Umbrella deductions (from assignment rate)")
        ubd_row("Gross contract income", ur.annual_gross_contract_income,
            f"{ua.days_per_week} days × {ua.weeks_per_year} weeks × £{ur.day_rate:,.2f}/day",
            is_total=True)
        ubd_row("Less: Umbrella margin", -ur.umbrella_margin_annual,
            f"£{ua.umbrella_margin_per_week:,.2f}/week × {ua.weeks_per_year} weeks",
            is_deduction=True)
        ubd_row("Less: Employer pension contribution", -ur.employer_pension_annual,
            f"{ua.employer_pension_rate:.1%} of qualifying earnings (£{ur.qualifying_earnings_base:,.0f})",
            is_deduction=True)
        ubd_row("Less: Employer NI", -ur.employer_ni,
            f"(Gross PAYE − £{ua.employer_ni_secondary_threshold:,.0f}) × {ua.employer_ni_rate:.1%} — solved algebraically",
            is_deduction=True)
        ubd_row("Less: Apprenticeship Levy", -ur.apprenticeship_levy,
            f"Gross PAYE × {ua.apprenticeship_levy_rate:.1%}",
            is_deduction=True)
        ubd_row("= Gross PAYE salary", ur.gross_paye_salary,
            f"£{u_gross_paye_daily:,.2f}/day · £{u_gross_paye_weekly:,.2f}/wk · £{u_gross_paye_monthly:,.2f}/mo",
            is_total=True)

        st.markdown("")

        ubd_header("Step 2 — Pre-tax deductions")
        ubd_row("Gross PAYE salary", ur.gross_paye_salary,
            "Starting point for employee deductions")
        ubd_row("Less: Employee pension (pre-tax)", -ur.employee_pension_pretax,
            f"{ua.employee_pension_rate:.1%} of qualifying earnings — deducted before tax",
            is_deduction=True)
        ubd_row("= Gross taxable pay", ur.gross_taxable_pay,
            "Income subject to income tax and NI", is_total=True)

        st.markdown("")

        ubd_header("Step 3 — Income tax & employee NI")
        ubd_row("Gross taxable pay", ur.gross_taxable_pay,
            "Starting point for tax calculation")
        ubd_row("Less: Income tax (basic rate)", -ur.income_tax_basic,
            f"20% on earnings £{ua.personal_allowance:,.0f}–£{ua.basic_rate_ceiling:,.0f}",
            is_deduction=True)
        ubd_row("Less: Income tax (higher rate)", -ur.income_tax_higher,
            f"40% on earnings £{ua.basic_rate_ceiling:,.0f}–£{ua.higher_rate_ceiling:,.0f}",
            is_deduction=True)
        ubd_row("Less: Income tax (additional rate)", -ur.income_tax_additional,
            f"45% on earnings above £{ua.higher_rate_ceiling:,.0f}",
            is_deduction=True)
        ubd_row("Less: Employee NI (standard)", -ur.employee_ni_standard,
            f"{ua.ni_rate_standard:.0%} on earnings £{ua.ni_primary_threshold:,.0f}–£{ua.ni_upper_earnings_limit:,.0f}",
            is_deduction=True)
        ubd_row("Less: Employee NI (above UEL)", -ur.employee_ni_above_uel,
            f"{ua.ni_rate_above_uel:.0%} on earnings above £{ua.ni_upper_earnings_limit:,.0f}",
            is_deduction=True)
        ubd_row("Less: Employee pension (post-tax)", -ur.employee_pension_posttax,
            "Relief at source only — deducted after tax" if ua.pension_scheme_type == "Relief at source" else "Not applicable for this scheme type",
            is_deduction=True)
        ubd_row("= Net take-home (annual)", ur.annual_net,
            "Gross taxable pay minus all taxes and deductions", is_total=True)

    st.markdown("---")
    st.subheader("Tax & Deductions Summary")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Income tax", mfmt(ur.income_tax_paid))
    s2.metric("Employee NI", mfmt(ur.employee_ni_paid))
    s3.metric("Umbrella margin", mfmt(ur.umbrella_margin_paid))
    s4.metric("Your pension", mfmt(ur.employee_pension_contribution))
    s5.metric("Employer pension", mfmt(ur.employer_pension_contribution))

    with st.expander("Cost to Client"):
        for label, value in [
            ("Gross assignment rate (total cost to client)", ur.annual_gross_contract_income),
            ("  Of which: umbrella margin", ur.umbrella_margin_annual),
            ("  Of which: employer pension", ur.employer_pension_annual),
            ("  Of which: employer NI", ur.employer_ni),
            ("  Of which: apprenticeship levy", ur.apprenticeship_levy),
            ("  Of which: your gross PAYE salary", ur.gross_paye_salary),
            ("Your gross PAYE salary as % of assignment rate", None),
        ]:
            ca, cb = st.columns([3, 1])
            bold = "font-weight: bold;" if "assignment rate" in label.lower() or "total" in label.lower() else ""
            ca.markdown(f"<span style='{bold}'>{plabel(label)}</span>", unsafe_allow_html=True)
            if value is not None:
                cb.markdown(f"<span style='{bold}'>{fmt(value)}</span>", unsafe_allow_html=True)
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

        def sa_row(label, widget_fn, note=""):
            ca, cb, cc = st.columns([2, 1, 3])
            ca.markdown(f"<span style='font-size:0.95em;'>{label}</span>", unsafe_allow_html=True)
            with cb:
                result = widget_fn()
            cc.markdown(f"<span style='color:#888888;font-size:0.85em;'>{note}</span>", unsafe_allow_html=True)
            return result

        def sa_header(text):
            st.markdown(f"**{text}**")
            ca, cb, cc = st.columns([2, 1, 3])
            ca.markdown("<span style='color:#888;font-size:0.8em;'>Setting</span>", unsafe_allow_html=True)
            cb.markdown("<span style='color:#888;font-size:0.8em;'>Value</span>", unsafe_allow_html=True)
            cc.markdown("<span style='color:#888;font-size:0.8em;'>Note</span>", unsafe_allow_html=True)

        sa_header("Working pattern")
        s_days_per_week = sa_row("Days per week",
            lambda: st.number_input("", value=5.0, step=0.5, key="s_dpw", label_visibility="collapsed"),
            "Number of days you work per week")
        s_weeks_per_year = sa_row("Weeks per year",
            lambda: st.number_input("", value=46, step=1, key="s_wpy", label_visibility="collapsed"),
            "Used to calculate the equivalent day rate. For comparison with contractor rates, 46 weeks accounts for holiday and bank holidays.")
        s_hours_per_day = sa_row("Hours per day",
            lambda: st.number_input("", value=7.5, step=0.5, key="s_hpd", label_visibility="collapsed"),
            "Used to calculate hourly equivalent rate only")

        st.markdown("")
        sa_header("Employer NI")
        s_er_ni_rate = sa_row("Employer NI rate (%)",
            lambda: st.number_input("", value=ty["employer_ni_rate"] * 100, step=0.1, format="%.1f", key=f"s_er_ni_rate_{selected_year}", label_visibility="collapsed") / 100,
            "Paid by the employer on top of your salary — shown in the Cost to Employer section. Updates with tax year selection.")
        s_er_ni_threshold = sa_row("Secondary threshold (£/yr)",
            lambda: st.number_input("", value=float(ty["employer_ni_threshold"]), step=100.0, key=f"s_er_ni_threshold_{selected_year}", label_visibility="collapsed"),
            "Employer NI is only charged on salary above this amount. Updates with tax year selection.")

        st.markdown("")
        sa_header("Pension")
        s_pension_type = sa_row("Pension scheme type",
            lambda: st.selectbox("", ["Relief at source", "Net pay arrangement", "Salary sacrifice"], key="s_pension_type", label_visibility="collapsed"),
            "Relief at source: deducted post-tax, HMRC tops up at 20%. Net pay: deducted before tax and NI. Salary sacrifice: reduces gross salary, saves employee and employer NI.")
        s_ee_pension = sa_row("Employee contribution (%)",
            lambda: st.number_input("", value=13.5, step=0.5, format="%.1f", key="s_ee_pension", label_visibility="collapsed") / 100,
            "Your personal pension contribution as a percentage of qualifying earnings. NHS default is 13.5%.")
        s_er_pension = sa_row("Employer contribution (%)",
            lambda: st.number_input("", value=28.97, step=0.5, format="%.2f", key="s_er_pension", label_visibility="collapsed") / 100,
            "Employer pension contribution as a percentage of qualifying earnings. NHS employer default is 28.97%.")

        s_ni_passback = False
        if s_pension_type == "Salary sacrifice":
            s_ni_passback = sa_row("Employer passes NI saving to pension?",
                lambda: st.checkbox("", value=False, key="s_ni_passback", label_visibility="collapsed"),
                "If yes, the employer NI saving from salary sacrifice is added to your pension pot.")

        st.markdown("")
        sa_header("Other employer costs")
        s_sick_pay = sa_row("Employer sick pay liability (% of salary)",
            lambda: st.number_input("", value=2.0, step=0.5, format="%.1f", key="s_sick_pay", label_visibility="collapsed") / 100,
            "Estimated cost of paying salary during sick leave. 2% ≈ 5 days full pay per year. Shown in Cost to Employer section.")

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
    m1.metric(f"Net take-home ({psuffix})", mfmt(sr.annual_net))
    m2.metric("Monthly", f"£{sr.monthly_net:,.0f}")
    m3.metric("Daily equivalent", f"£{sr.daily_net:,.2f}")
    m4.metric("Effective tax rate", f"{sr.effective_tax_rate:.1%}")

    with st.expander("Full Breakdown"):

        def sbd_row(label, value, note="", is_deduction=False, is_total=False):
            ca, cb, cc = st.columns([3, 1, 3])
            if is_total:
                style = "font-weight: bold;"
            elif is_deduction:
                style = "color: #cc0000;"
            else:
                style = ""
            note_style = "color: #888888; font-size: 0.85em;"
            ca.markdown(f"<span style='{style}'>{label}</span>", unsafe_allow_html=True)
            cb.markdown(f"<span style='{style}'>{fmt(value)}</span>", unsafe_allow_html=True)
            cc.markdown(f"<span style='{note_style}'>{note}</span>", unsafe_allow_html=True)

        def sbd_header(text):
            st.markdown(f"**{text}**")
            ca, cb, cc = st.columns([3, 1, 3])
            ca.markdown("<span style='color:#888;font-size:0.8em;'>Description</span>", unsafe_allow_html=True)
            cb.markdown("<span style='color:#888;font-size:0.8em;'>Amount</span>", unsafe_allow_html=True)
            cc.markdown("<span style='color:#888;font-size:0.8em;'>Note</span>", unsafe_allow_html=True)

        sbd_header("Step 1 — Gross salary")
        sbd_row("Gross annual salary", s_salary,
            "Contracted salary before any deductions", is_total=True)
        sbd_row("Equivalent day rate", sr.equivalent_day_rate,
            f"£{s_salary:,.0f} ÷ ({sa.days_per_week} days × {sa.weeks_per_year} weeks)")

        st.markdown("")

        sbd_header("Step 2 — Pre-tax deductions")
        sbd_row("Gross salary", s_salary, "Starting point")
        sbd_row("Less: Employee pension (pre-tax)", -sr.employee_pension_pretax,
            f"{sa.employee_pension_rate:.1%} of qualifying earnings — deducted before tax",
            is_deduction=True)
        sbd_row("= Gross taxable pay", sr.gross_taxable_pay,
            "Income subject to income tax and NI", is_total=True)

        st.markdown("")

        sbd_header("Step 3 — Income tax & employee NI")
        sbd_row("Gross taxable pay", sr.gross_taxable_pay, "Starting point for tax")
        sbd_row("Less: Income tax (basic rate)", -sr.income_tax_basic,
            f"20% on earnings £{sa.personal_allowance:,.0f}–£{sa.basic_rate_ceiling:,.0f}",
            is_deduction=True)
        sbd_row("Less: Income tax (higher rate)", -sr.income_tax_higher,
            f"40% on earnings £{sa.basic_rate_ceiling:,.0f}–£{sa.higher_rate_ceiling:,.0f}",
            is_deduction=True)
        sbd_row("Less: Income tax (additional rate)", -sr.income_tax_additional,
            f"45% on earnings above £{sa.higher_rate_ceiling:,.0f}",
            is_deduction=True)
        sbd_row("Less: Employee NI (standard)", -sr.employee_ni_standard,
            f"{sa.ni_rate_standard:.0%} on earnings £{sa.ni_primary_threshold:,.0f}–£{sa.ni_upper_earnings_limit:,.0f}",
            is_deduction=True)
        sbd_row("Less: Employee NI (above UEL)", -sr.employee_ni_above_uel,
            f"{sa.ni_rate_above_uel:.0%} on earnings above £{sa.ni_upper_earnings_limit:,.0f}",
            is_deduction=True)
        sbd_row("Less: Employee pension (post-tax)", -sr.employee_pension_posttax,
            "Relief at source only — HMRC tops up at 20%" if sa.pension_scheme_type == "Relief at source" else "Not applicable for this scheme type",
            is_deduction=True)
        sbd_row("= Net take-home (annual)", sr.annual_net,
            "Gross taxable pay minus all taxes and deductions", is_total=True)

        st.markdown("")

        sbd_header("Pension memo")
        sbd_row("Your pension contribution", sr.employee_pension_contribution,
            f"{sa.employee_pension_rate:.1%} of qualifying earnings")
        sbd_row("HMRC basic rate top-up", sr.hmrc_basic_rate_topup,
            "Relief at source only — 20% added by HMRC to pension pot")
        sbd_row("Employer NI saving to pension", sr.employer_ni_saving_to_pension,
            "Salary sacrifice only — employer passes NI saving to pension")
        sbd_row("Total pension pot funded", sr.total_pension_pot,
            "Your contribution + any top-ups", is_total=True)

    st.markdown("---")
    st.subheader("Tax & Deductions Summary")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Income tax", mfmt(sr.income_tax_paid))
    s2.metric("Employee NI", mfmt(sr.employee_ni_paid))
    s3.metric("Your pension", mfmt(sr.employee_pension_contribution))
    s4.metric("Employer pension", mfmt(sr.employer_pension_contribution))
    s5.metric("Employer NI", mfmt(sr.employer_ni))

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
            ca.markdown(f"<span style='{bold}'>{plabel(label)}</span>", unsafe_allow_html=True)
            if "day rate" in label.lower():
                cb.markdown(f"<span style='{bold}'>£{value:,.2f}/day</span>", unsafe_allow_html=True)
            else:
                cb.markdown(f"<span style='{bold}'>{fmt(value)}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Figures are indicative only. Tax rates based on published HMRC rates. Not financial advice.")
