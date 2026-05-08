"""
Rate Calculator — Ltd Co, Umbrella, Salaried.
Tax year selector and display period selector drive all three tabs.
localStorage persistence for user-specific inputs via streamlit-local-storage.
"""

import streamlit as st
from streamlit_local_storage import LocalStorage
from calculator import calculate as umbrella_calculate, UmbrellaAssumptions
from salaried_calculator import calculate as salaried_calculate, SalariedAssumptions
from ltd_co_calculator import calculate as ltd_co_calculate, LtdCoAssumptions
from tax_years import TAX_YEARS, TAX_YEAR_OPTIONS, DEFAULT_TAX_YEAR

st.set_page_config(
    page_title="Rate Calculator",
    page_icon="🧮",
    layout="wide",
)

# ── localStorage — read all saved values before any widgets render ────────────
_ls = LocalStorage()

def _ls_get(key, default):
    """Read a value from localStorage, falling back to default if absent."""
    val = _ls.getItem(key)
    if val is None:
        return default
    try:
        if isinstance(default, bool):
            return str(val).lower() == "true"
        elif isinstance(default, float):
            return float(val)
        elif isinstance(default, int):
            return int(float(val))
        else:
            return val
    except (ValueError, TypeError):
        return default

def _ls_set(key, value):
    _ls.setItem(key, str(value))

# Read all persisted values up-front
p_l_rate_period   = _ls_get("l_rate_period",   "Per Day")
p_l_rate_input    = _ls_get("l_rate_input",     440.0)
p_l_dpw           = _ls_get("l_dpw",            5.0)
p_l_hpd           = _ls_get("l_hpd",            7.5)
p_l_leave         = _ls_get("l_leave",          19)
p_l_bh            = _ls_get("l_bh",             11)
p_l_pi            = _ls_get("l_pi",             1200)
p_l_life          = _ls_get("l_life",           864)
p_l_ci            = _ls_get("l_ci",             600)
p_l_accountancy   = _ls_get("l_accountancy",    1800)
p_l_other         = _ls_get("l_other",          1000)
p_l_pension       = _ls_get("l_pension",        6000)

p_u_rate_period   = _ls_get("u_rate_period",    "Per Day")
p_u_rate_input    = _ls_get("u_rate_input",     500.0)
p_u_dpw           = _ls_get("u_dpw",            5.0)
p_u_hpd           = _ls_get("u_hpd",            7.5)
p_u_leave         = _ls_get("u_leave",          19)
p_u_bh            = _ls_get("u_bh",             11)

p_s_salary        = _ls_get("s_salary",         98500)
p_s_dpw           = _ls_get("s_dpw",            5.0)
p_s_hpd           = _ls_get("s_hpd",            7.5)
p_s_leave         = _ls_get("s_leave",          19)
p_s_bh            = _ls_get("s_bh",             11)
p_s_pension_type  = _ls_get("s_pension_type",   "Relief at source")
p_s_ee_pension    = _ls_get("s_ee_pension",     13.5)

# Validate selectbox values against allowed options
_l_rate_period_opts = ["Per Day", "Per Week", "Per Month", "Per Year"]
_u_rate_period_opts = ["Per Day", "Per Week", "Per Month", "Per Year"]
_s_pension_opts     = ["Relief at source", "Net pay arrangement", "Salary sacrifice"]
if p_l_rate_period not in _l_rate_period_opts: p_l_rate_period = "Per Day"
if p_u_rate_period not in _u_rate_period_opts: p_u_rate_period = "Per Day"
if p_s_pension_type not in _s_pension_opts:    p_s_pension_type = "Relief at source"

# ── Page header ───────────────────────────────────────────────────────────────
st.title("🧮 Rate Calculator")

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
    if display_period == "Per Year":
        return f"£{value:,.2f}"
    elif display_period == "Per Month":
        return f"£{value / 12:,.2f}"
    else:
        return f"£{value / 52:,.2f}"

def mfmt(value):
    if display_period == "Per Year":
        return f"£{value:,.0f}"
    elif display_period == "Per Month":
        return f"£{value / 12:,.0f}"
    else:
        return f"£{value / 52:,.2f}"

def plabel(label):
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
            _l_rate_period_opts,
            index=_l_rate_period_opts.index(p_l_rate_period),
            key="l_rate_period",
            help="Select how your rate is quoted. Converted to a daily rate before calculating.",
        )
        if l_rate_period != p_l_rate_period:
            _ls_set("l_rate_period", l_rate_period)

    with col_input:
        l_rate_labels = {"Per Day": "Day Rate (£/day)", "Per Week": "Weekly Rate (£/week)",
                         "Per Month": "Monthly Rate (£/month)", "Per Year": "Annual Rate (£/year)"}
        # Only restore the saved rate value when the saved period matches the current period selection,
        # to avoid showing a day-rate figure in the weekly field after a period switch.
        l_rate_default = p_l_rate_input if l_rate_period == p_l_rate_period else \
            {"Per Day": 440.0, "Per Week": 2200.0, "Per Month": 9533.0, "Per Year": 114400.0}[l_rate_period]
        l_rate_input = st.number_input(
            l_rate_labels[l_rate_period],
            min_value=1.0, max_value=500_000.0,
            value=float(l_rate_default),
            step=0.50, format="%.2f",
            help="The rate your Ltd Co invoices / receives from the client or agency.",
            key="l_rate_input",
        )
        if l_rate_input != p_l_rate_input:
            _ls_set("l_rate_input", l_rate_input)

    with st.expander("Assumptions — click to edit"):

        def a_row(label, widget_fn, note=""):
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
            lambda: st.number_input("", value=p_l_dpw, step=0.5, key="l_dpw", label_visibility="collapsed"),
            "Number of days you work per week")
        l_hours_per_day = a_row("Hours per day",
            lambda: st.number_input("", value=p_l_hpd, step=0.5, key="l_hpd", label_visibility="collapsed"),
            "Used to calculate hourly equivalent rate only")
        l_leave_days = a_row("Annual leave days",
            lambda: st.number_input("", value=p_l_leave, step=1, key="l_leave", label_visibility="collapsed"),
            "Unpaid holidays per year, excluding bank holidays.")
        l_bank_holidays = a_row("Bank holidays",
            lambda: st.number_input("", value=p_l_bh, step=1, key="l_bh", label_visibility="collapsed"),
            "Unpaid bank holidays per year.")

        if l_days_per_week != p_l_dpw:   _ls_set("l_dpw",   l_days_per_week)
        if l_hours_per_day != p_l_hpd:   _ls_set("l_hpd",   l_hours_per_day)
        if l_leave_days    != p_l_leave:  _ls_set("l_leave", l_leave_days)
        if l_bank_holidays != p_l_bh:     _ls_set("l_bh",    l_bank_holidays)

        l_weeks_off = (l_leave_days + l_bank_holidays) / l_days_per_week if l_days_per_week > 0 else 0
        l_weeks_per_year = round(52 - l_weeks_off, 1)
        ca_wp, cb_wp, cc_wp = st.columns([2, 1, 3])
        ca_wp.markdown("<span style='font-size:0.95em;'>Billable weeks per year</span>", unsafe_allow_html=True)
        cb_wp.markdown(f"<span style='font-weight:bold;'>{l_weeks_per_year:.1f}</span>", unsafe_allow_html=True)
        cc_wp.markdown(f"<span style='color:#888888;font-size:0.85em;'>52 − ({l_leave_days:.0f} + {l_bank_holidays:.0f}) days ÷ {l_days_per_week:.0f} days/week</span>", unsafe_allow_html=True)

        st.markdown("")
        a_header("Director salary & tax")
        l_director_salary = a_row("Director salary (£/yr)",
            lambda: st.number_input("", value=float(ty["personal_allowance"]), step=100.0, key=f"l_salary_{selected_year}", label_visibility="collapsed"),
            "Set at personal allowance by default — no income tax and minimal employer NI on the salary itself")
        l_corp_tax = a_row("Corporation tax rate (%)",
            lambda: st.number_input("", value=ty["corporation_tax_rate"] * 100, step=1.0, format="%.1f", key=f"l_corp_tax_{selected_year}", label_visibility="collapsed") / 100,
            f"{ty['corporation_tax_rate']:.0%} is the HMRC rate for {selected_year}. Main rate 25% on profits ≥ £250k. Small profits relief may apply below £50k — check with your accountant")
        l_div_allowance = a_row("Dividend allowance (£/yr)",
            lambda: st.number_input("", value=float(ty["dividend_allowance"]), step=100.0, key=f"l_div_allowance_{selected_year}", label_visibility="collapsed"),
            f"£{ty['dividend_allowance']:,.0f} is the HMRC rate for {selected_year}. Dividends within this allowance are tax-free.")

        st.markdown("")
        a_header("Employer NI")
        l_er_ni_rate = a_row("Employer NI rate (%)",
            lambda: st.number_input("", value=ty["employer_ni_rate"] * 100, step=0.1, format="%.1f", key=f"l_er_ni_rate_{selected_year}", label_visibility="collapsed") / 100,
            f"{ty['employer_ni_rate']:.1%} is the HMRC rate for {selected_year}. Charged on director salary above the secondary threshold.")
        l_er_ni_threshold = a_row("Secondary threshold (£/yr)",
            lambda: st.number_input("", value=float(ty["employer_ni_threshold"]), step=100.0, key=f"l_er_ni_threshold_{selected_year}", label_visibility="collapsed"),
            f"£{ty['employer_ni_threshold']:,.0f} is the HMRC rate for {selected_year}. Salary below this is not subject to employer NI.")

        st.markdown("")
        a_header("Business expenses & pension")
        l_pi = a_row("Professional indemnity insurance (£/yr)",
            lambda: st.number_input("", value=p_l_pi, step=100, key="l_pi", label_visibility="collapsed"),
            "Enter your yearly premium. Typical contractor cost — check your actual quote.")
        l_life = a_row("Relevant Life insurance (£/yr)",
            lambda: st.number_input("", value=p_l_life, step=50, key="l_life", label_visibility="collapsed"),
            "Company-paid life cover. Premiums paid from pre-tax profit.")
        l_ci = a_row("Critical illness / IP insurance (£/yr)",
            lambda: st.number_input("", value=p_l_ci, step=50, key="l_ci", label_visibility="collapsed"),
            "Income protection if you cannot work. Contractor equivalent of employer sick pay.")
        l_accountancy = a_row("Accountancy fees (£/yr)",
            lambda: st.number_input("", value=p_l_accountancy, step=100, key="l_accountancy", label_visibility="collapsed"),
            "Adjust to your actual accountant's fee.")
        l_other = a_row("Other business expenses (£/yr)",
            lambda: st.number_input("", value=p_l_other, step=100, key="l_other", label_visibility="collapsed"),
            "Phone, software, home office, travel etc.")
        l_pension = a_row("Employer pension contribution (£/yr)",
            lambda: st.number_input("", value=p_l_pension, step=100, key="l_pension", label_visibility="collapsed"),
            "Company contribution paid directly into your pension before corporation tax. Adjust to your actual contribution.")

        if l_pi          != p_l_pi:          _ls_set("l_pi",          l_pi)
        if l_life        != p_l_life:        _ls_set("l_life",        l_life)
        if l_ci          != p_l_ci:          _ls_set("l_ci",          l_ci)
        if l_accountancy != p_l_accountancy: _ls_set("l_accountancy", l_accountancy)
        if l_other       != p_l_other:       _ls_set("l_other",       l_other)
        if l_pension     != p_l_pension:     _ls_set("l_pension",     l_pension)

    # Convert input rate to daily
    if l_rate_period == "Per Day":
        l_day_rate = l_rate_input
    elif l_rate_period == "Per Week":
        l_day_rate = l_rate_input / l_days_per_week
    elif l_rate_period == "Per Month":
        l_day_rate = l_rate_input / (l_weeks_per_year * l_days_per_week / 12)
    else:
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
        higher_rate_band_upper=ty["higher_rate_ceiling"],
        personal_allowance=ty["personal_allowance"],
        income_tax_basic=ty["income_tax_basic"],
        income_tax_higher=ty["income_tax_higher"],
        income_tax_additional=ty["income_tax_additional"],
        ni_primary_threshold=ty["ni_primary_threshold"],
        ni_upper_earnings_limit=ty["ni_upper_earnings_limit"],
        ni_rate_standard=ty["ni_rate_standard"],
        ni_rate_above_uel=ty["ni_rate_above_uel"],
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
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(f"Net take-home ({psuffix})", mfmt(lr.annual_net))
    m2.metric("Monthly", f"£{lr.monthly_net:,.0f}")
    m3.metric("Weekly", f"£{lr.annual_net / 52:,.0f}")
    m4.metric("Daily equivalent", f"£{lr.daily_net:,.2f}")
    m5.metric("Effective tax rate", f"{lr.effective_tax_rate:.1%}")

    with st.expander("Full Breakdown"):

        def bd_row(label, value, note="", is_deduction=False, is_total=False):
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

        bd_header("Step 2 — Personal income")
        bd_row("Director salary received", lr.director_salary,
            "Paid via payroll — within personal allowance")
        bd_row("Dividends drawn", lr.dividends_drawn,
            "Full distributable profit drawn as dividends")
        bd_row("Total personal income", lr.total_personal_income,
            "Salary + dividends", is_total=True)

        st.markdown("")

        bd_header("Step 3 — Personal tax")
        bd_row("Less: Income tax on salary", -lr.income_tax_on_salary,
            f"Salary at personal allowance — no income tax due." if lr.income_tax_on_salary == 0 else f"(£{la.director_salary:,.0f} − £{la.personal_allowance:,.0f}) × {la.income_tax_basic:.0%}",
            is_deduction=True)
        bd_row("Less: Employee NI on salary", -lr.employee_ni_on_salary,
            f"Salary at or below NI primary threshold £{la.ni_primary_threshold:,.0f} — no employee NI due." if lr.employee_ni_on_salary == 0 else f"(£{la.director_salary:,.0f} − £{la.ni_primary_threshold:,.0f}) × {la.ni_rate_standard:.0%}",
            is_deduction=True)
        bd_row("Less: Dividend tax", -lr.dividend_tax,
            f"Allowance £{la.dividend_allowance:,.0f} tax-free | Basic {la.dividend_basic_rate:.2%} £{lr.dividends_basic_rate_band * la.dividend_basic_rate:,.0f} | Higher {la.dividend_higher_rate:.2%} £{lr.dividends_higher_rate_band * la.dividend_higher_rate:,.0f}",
            is_deduction=True)
        bd_row("= Net take-home (annual)", lr.annual_net,
            "Salary + dividends minus all personal tax", is_total=True)

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
            _u_rate_period_opts,
            index=_u_rate_period_opts.index(p_u_rate_period),
            key="u_rate_period",
            help="Select how your rate is quoted. Converted to a daily rate before calculating.",
        )
        if u_rate_period != p_u_rate_period:
            _ls_set("u_rate_period", u_rate_period)

    with col_input:
        u_rate_labels = {"Per Day": "Day Rate (£/day)", "Per Week": "Weekly Rate (£/week)",
                         "Per Month": "Monthly Rate (£/month)", "Per Year": "Annual Rate (£/year)"}
        u_rate_default = p_u_rate_input if u_rate_period == p_u_rate_period else \
            {"Per Day": 500.0, "Per Week": 2500.0, "Per Month": 10833.0, "Per Year": 130000.0}[u_rate_period]
        u_rate_input = st.number_input(
            u_rate_labels[u_rate_period],
            min_value=1.0, max_value=500_000.0,
            value=float(u_rate_default),
            step=0.50, format="%.2f",
            help="The rate you invoice via the agency / umbrella.",
            key="u_rate_input",
        )
        if u_rate_input != p_u_rate_input:
            _ls_set("u_rate_input", u_rate_input)

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
            lambda: st.number_input("", value=p_u_dpw, step=0.5, key="u_dpw", label_visibility="collapsed"),
            "Number of days you work per week")
        u_hours_per_day = ua_row("Hours per day",
            lambda: st.number_input("", value=p_u_hpd, step=0.5, key="u_hpd", label_visibility="collapsed"),
            "Used to calculate hourly equivalent rate only")
        u_leave_days = ua_row("Annual leave days",
            lambda: st.number_input("", value=p_u_leave, step=1, key="u_leave", label_visibility="collapsed"),
            "Unpaid holidays per year, excluding bank holidays. Holiday pay under umbrella does not add income — it is built into the assignment rate and redistributed by the umbrella.")
        u_bank_holidays = ua_row("Bank holidays",
            lambda: st.number_input("", value=p_u_bh, step=1, key="u_bh", label_visibility="collapsed"),
            "Unpaid bank holidays per year.")

        if u_days_per_week != p_u_dpw:   _ls_set("u_dpw",   u_days_per_week)
        if u_hours_per_day != p_u_hpd:   _ls_set("u_hpd",   u_hours_per_day)
        if u_leave_days    != p_u_leave:  _ls_set("u_leave", u_leave_days)
        if u_bank_holidays != p_u_bh:     _ls_set("u_bh",    u_bank_holidays)

        u_weeks_off = (u_leave_days + u_bank_holidays) / u_days_per_week if u_days_per_week > 0 else 0
        u_weeks_per_year = round(52 - u_weeks_off, 1)
        ca_wp, cb_wp, cc_wp = st.columns([2, 1, 3])
        ca_wp.markdown("<span style='font-size:0.95em;'>Billable weeks per year</span>", unsafe_allow_html=True)
        cb_wp.markdown(f"<span style='font-weight:bold;'>{u_weeks_per_year:.1f}</span>", unsafe_allow_html=True)
        cc_wp.markdown(f"<span style='color:#888888;font-size:0.85em;'>52 − ({u_leave_days:.0f} + {u_bank_holidays:.0f}) days ÷ {u_days_per_week:.0f} days/week</span>", unsafe_allow_html=True)

        st.markdown("")
        ua_header("Umbrella costs")
        u_margin_annual = ua_row("Umbrella margin (£/yr)",
            lambda: st.number_input("", value=1_300, step=50, key="u_margin", label_visibility="collapsed"),
            "Annual umbrella fee charged 52 weeks/year regardless of billable weeks. Typical £15–£30/week. Default is £25 × 52 weeks.")
        u_levy_rate = ua_row("Apprenticeship Levy (%)",
            lambda: st.number_input("", value=0.5, step=0.1, format="%.1f", key="u_levy", label_visibility="collapsed") / 100,
            "0.5% of your gross PAYE salary, passed through by most umbrellas. Set to 0 if your umbrella does not charge this.")

        st.markdown("")
        ua_header("Employer NI")
        u_er_ni_rate = ua_row("Employer NI rate (%)",
            lambda: st.number_input("", value=ty["employer_ni_rate"] * 100, step=0.1, format="%.1f", key=f"u_er_ni_rate_{selected_year}", label_visibility="collapsed") / 100,
            f"{ty['employer_ni_rate']:.1%} is the HMRC rate for {selected_year}. Under umbrella this is deducted from your assignment rate, not paid by the client on top.")
        u_er_ni_threshold = ua_row("Secondary threshold (£/yr)",
            lambda: st.number_input("", value=float(ty["employer_ni_threshold"]), step=100.0, key=f"u_er_ni_threshold_{selected_year}", label_visibility="collapsed"),
            f"£{ty['employer_ni_threshold']:,.0f} is the HMRC rate for {selected_year}. Employer NI only applies to gross PAYE salary above this amount.")

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
            "Statutory minimum is 3%. Deducted from your assignment rate in Step 1 — this is not new money from the client, it reduces your gross PAYE salary.")

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
    else:
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
        umbrella_margin_per_week=u_margin_annual / 52,
        employer_ni_secondary_threshold=u_er_ni_threshold,
        employer_ni_rate=u_er_ni_rate,
        apprenticeship_levy_rate=u_levy_rate,
        pension_scheme_type=u_pension_type_full,
        employee_pension_rate=u_ee_pension,
        employer_pension_rate=u_er_pension,
        employer_passes_ni_saving_to_pension=u_ni_passback,
    )
    ur = umbrella_calculate(u_day_rate, ua)

    u_gross_paye_daily = ur.gross_paye_salary / ur.days_per_year
    u_gross_paye_weekly = ur.gross_paye_salary / 52
    u_gross_paye_monthly = ur.gross_paye_salary / 12

    st.markdown("---")
    st.subheader("Net Take-Home")
    m1, m2, m3, m4 = st.columns(4)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(f"Net take-home ({psuffix})", mfmt(ur.annual_net))
    m2.metric("Monthly", f"£{ur.monthly_net:,.0f}")
    m3.metric("Weekly", f"£{ur.annual_net / 52:,.0f}")
    m4.metric("Daily equivalent", f"£{ur.daily_net:,.2f}")
    m5.metric("Effective tax rate", f"{ur.effective_tax_rate:.1%}")

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
            f"£{ua.umbrella_margin_per_week:,.2f}/week × 52 weeks (charged year-round, not just billable weeks)",
            is_deduction=True)
        ubd_row("Less: Employer pension contribution", -ur.employer_pension_annual,
            f"{ua.employer_pension_rate:.1%} of qualifying earnings (£{ur.qualifying_earnings_base:,.0f})",
            is_deduction=True)
        ubd_row("Less: Employer NI", -ur.employer_ni,
            f"(Gross PAYE − £{ua.employer_ni_secondary_threshold:,.0f}) × {ua.employer_ni_rate:.1%}. Gross PAYE is unknown until NI and levy are deducted, so the equation is solved simultaneously: assignment rate minus margin equals Gross PAYE plus NI plus levy, all expressed as a function of Gross PAYE.",
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
        ubd_row("Less: Income tax", -ur.total_income_tax,
            f"Basic 20% £{ur.income_tax_basic:,.0f} | Higher 40% £{ur.income_tax_higher:,.0f} | Additional 45% £{ur.income_tax_additional:,.0f}",
            is_deduction=True)
        ubd_row("Less: Employee NI", -ur.total_employee_ni,
            f"Standard {ua.ni_rate_standard:.0%} £{ur.employee_ni_standard:,.0f} | Above UEL {ua.ni_rate_above_uel:.0%} £{ur.employee_ni_above_uel:,.0f}",
            is_deduction=True)
        ubd_row("Less: Employee pension (post-tax)", -ur.employee_pension_posttax,
            "Relief at source only — deducted after tax" if ua.pension_scheme_type == "Relief at source" else "Not applicable for this scheme type",
            is_deduction=True)
        ubd_row("= Net take-home (annual)", ur.annual_net,
            "Gross taxable pay minus all taxes and deductions", is_total=True)

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
            min_value=10_000, max_value=500_000, value=p_s_salary, step=500,
            help="Your gross contracted salary before any deductions.",
            key="s_salary",
        )
        if s_salary != p_s_salary:
            _ls_set("s_salary", s_salary)

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
            lambda: st.number_input("", value=p_s_dpw, step=0.5, key="s_dpw", label_visibility="collapsed"),
            "Number of days you work per week")
        s_hours_per_day = sa_row("Hours per day",
            lambda: st.number_input("", value=p_s_hpd, step=0.5, key="s_hpd", label_visibility="collapsed"),
            "Used to calculate the hourly equivalent rate only")
        s_leave_days = sa_row("Annual leave days",
            lambda: st.number_input("", value=p_s_leave, step=1, key="s_leave", label_visibility="collapsed"),
            "Paid holiday days per year, excluding bank holidays. UK statutory minimum is 20 days.")
        s_bank_holidays = sa_row("Bank holidays",
            lambda: st.number_input("", value=p_s_bh, step=1, key="s_bh", label_visibility="collapsed"),
            "Public bank holidays per year. England & Wales has 8 statutory days plus 3 additional common holidays.")

        if s_days_per_week != p_s_dpw:   _ls_set("s_dpw",   s_days_per_week)
        if s_hours_per_day != p_s_hpd:   _ls_set("s_hpd",   s_hours_per_day)
        if s_leave_days    != p_s_leave:  _ls_set("s_leave", s_leave_days)
        if s_bank_holidays != p_s_bh:     _ls_set("s_bh",    s_bank_holidays)

        s_weeks_off = (s_leave_days + s_bank_holidays) / s_days_per_week if s_days_per_week > 0 else 0
        s_weeks_per_year = round(52 - s_weeks_off, 1)
        ca_wp, cb_wp, cc_wp = st.columns([2, 1, 3])
        ca_wp.markdown("<span style='font-size:0.95em;'>Worked weeks per year</span>", unsafe_allow_html=True)
        cb_wp.markdown(f"<span style='font-weight:bold;'>{s_weeks_per_year:.1f}</span>", unsafe_allow_html=True)
        cc_wp.markdown(f"<span style='color:#888888;font-size:0.85em;'>52 − ({s_leave_days:.0f} + {s_bank_holidays:.0f}) days ÷ {s_days_per_week:.0f} days/week</span>", unsafe_allow_html=True)

        st.markdown("")
        sa_header("Employer NI")
        s_er_ni_rate = sa_row("Employer NI rate (%)",
            lambda: st.number_input("", value=ty["employer_ni_rate"] * 100, step=0.1, format="%.1f", key=f"s_er_ni_rate_{selected_year}", label_visibility="collapsed") / 100,
            f"{ty['employer_ni_rate']:.1%} is the HMRC rate for {selected_year}. Paid by employer on top of your salary.")
        s_er_ni_threshold = sa_row("Secondary threshold (£/yr)",
            lambda: st.number_input("", value=float(ty["employer_ni_threshold"]), step=100.0, key=f"s_er_ni_threshold_{selected_year}", label_visibility="collapsed"),
            f"£{ty['employer_ni_threshold']:,.0f} is the HMRC rate for {selected_year}. Salary below this is not subject to employer NI.")

        st.markdown("")
        sa_header("Pension")
        s_pension_type = sa_row("Pension scheme type",
            lambda: st.selectbox("", _s_pension_opts, index=_s_pension_opts.index(p_s_pension_type), key="s_pension_type", label_visibility="collapsed"),
            "Relief at source: deducted post-tax, HMRC tops up at 20%. Net pay: deducted before tax and NI. Salary sacrifice: reduces gross salary, saves employee and employer NI.")
        s_ee_pension = sa_row("Employee contribution (%)",
            lambda: st.number_input("", value=p_s_ee_pension, step=0.5, format="%.1f", key="s_ee_pension", label_visibility="collapsed") / 100,
            "Your personal pension contribution as a percentage of qualifying earnings. NHS default is 13.5%.")

        if s_pension_type    != p_s_pension_type:   _ls_set("s_pension_type", s_pension_type)
        if s_ee_pension * 100 != p_s_ee_pension:    _ls_set("s_ee_pension",   s_ee_pension * 100)

        s_ni_passback = False
        if s_pension_type == "Salary sacrifice":
            s_ni_passback = sa_row("Employer passes NI saving to pension?",
                lambda: st.checkbox("", value=False, key="s_ni_passback", label_visibility="collapsed"),
                "If yes, the employer NI saving from salary sacrifice is added to your pension pot.")

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
        employer_passes_ni_saving_to_pension=s_ni_passback,
    )
    sr = salaried_calculate(s_salary, sa)

    st.markdown("---")
    st.subheader("Net Take-Home")
    m1, m2, m3, m4 = st.columns(4)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(f"Net take-home ({psuffix})", mfmt(sr.annual_net))
    m2.metric("Monthly", f"£{sr.monthly_net:,.0f}")
    m3.metric("Weekly", f"£{sr.annual_net / 52:,.0f}")
    m4.metric("Daily equivalent", f"£{sr.daily_net:,.2f}")
    m5.metric("Effective tax rate", f"{sr.effective_tax_rate:.1%}")

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
        sbd_row("Less: Income tax", -(sr.income_tax_basic + sr.income_tax_higher + sr.income_tax_additional),
            f"Basic 20% £{sr.income_tax_basic:,.0f} | Higher 40% £{sr.income_tax_higher:,.0f} | Additional 45% £{sr.income_tax_additional:,.0f}",
            is_deduction=True)
        sbd_row("Less: Employee NI", -(sr.employee_ni_standard + sr.employee_ni_above_uel),
            f"Standard {sa.ni_rate_standard:.0%} £{sr.employee_ni_standard:,.0f} | Above UEL {sa.ni_rate_above_uel:.0%} £{sr.employee_ni_above_uel:,.0f}",
            is_deduction=True)
        sbd_row("Less: Employee pension (post-tax)", -sr.employee_pension_posttax,
            "Relief at source only — HMRC tops up at 20%" if sa.pension_scheme_type == "Relief at source" else "Not applicable for this scheme type",
            is_deduction=True)
        sbd_row("= Net take-home (annual)", sr.annual_net,
            "Gross taxable pay minus all taxes and deductions", is_total=True)

    st.markdown("---")
    st.caption("Figures are indicative only. Tax rates based on published HMRC rates. Not financial advice.")
