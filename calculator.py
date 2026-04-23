"""
Umbrella Rate Calculator — core calculation module.
Mirrors the logic in the 'Inside IR35 (Umbrella)' sheet of rate_calculator_v10.xlsx.
All monetary values in GBP, annual unless noted.
"""

from dataclasses import dataclass, field


@dataclass
class UmbrellaAssumptions:
    # Working pattern
    days_per_week: float = 5
    weeks_per_year: float = 46
    hours_per_day: float = 7.5

    # PAYE tax bands (2024/25)
    personal_allowance: float = 12_570
    basic_rate_ceiling: float = 50_270
    higher_rate_ceiling: float = 125_140
    income_tax_basic: float = 0.20
    income_tax_higher: float = 0.40
    income_tax_additional: float = 0.45

    # Employee NI (2024/25)
    ni_primary_threshold: float = 12_570
    ni_rate_standard: float = 0.08
    ni_upper_earnings_limit: float = 50_270
    ni_rate_above_uel: float = 0.02

    # Umbrella-specific
    umbrella_margin_per_week: float = 25
    employer_ni_secondary_threshold: float = 9_100
    employer_ni_rate: float = 0.138
    apprenticeship_levy_rate: float = 0.005

    # Auto-enrolment pension
    pension_scheme_type: str = "Net pay arrangement"   # or "Relief at source" or "Salary sacrifice"
    qualifying_earnings_lower: float = 6_240
    qualifying_earnings_upper: float = 50_270
    employer_pension_rate: float = 0.03
    employee_pension_rate: float = 0.05
    employer_passes_ni_saving_to_pension: bool = False


@dataclass
class UmbrellaResult:
    # Inputs
    day_rate: float = 0
    assumptions: UmbrellaAssumptions = field(default_factory=UmbrellaAssumptions)

    # Working pattern
    days_per_year: float = 0
    hours_per_year: float = 0
    annual_gross_contract_income: float = 0

    # Step 1 — umbrella deductions
    umbrella_margin_annual: float = 0
    employer_ni: float = 0
    apprenticeship_levy: float = 0
    gross_paye_salary: float = 0

    # Pension base
    qualifying_earnings_base: float = 0

    # Step 2 — pre-tax deductions
    employee_pension_pretax: float = 0
    gross_taxable_pay: float = 0

    # Step 3 — income tax
    taxable_income: float = 0
    income_tax_basic: float = 0
    income_tax_higher: float = 0
    income_tax_additional: float = 0
    total_income_tax: float = 0

    # Step 3 — employee NI
    employee_ni_standard: float = 0
    employee_ni_above_uel: float = 0
    total_employee_ni: float = 0

    # Step 3b — post-tax deductions
    employee_pension_posttax: float = 0
    employer_ni_saving_salary_sacrifice: float = 0
    employer_ni_saving_to_pension: float = 0
    hmrc_basic_rate_topup: float = 0
    total_pension_pot: float = 0

    # Net take-home
    annual_net: float = 0
    monthly_net: float = 0
    daily_net: float = 0
    hourly_net: float = 0

    # Cost to client
    employer_pension_annual: float = 0
    total_cost_to_client: float = 0
    gross_salary_pct_of_client_cost: float = 0

    # Effective rates
    effective_tax_rate: float = 0
    income_tax_paid: float = 0
    employee_ni_paid: float = 0
    umbrella_margin_paid: float = 0
    employee_pension_contribution: float = 0
    employer_pension_contribution: float = 0


def calculate(day_rate: float, assumptions: UmbrellaAssumptions = None) -> UmbrellaResult:
    a = assumptions or UmbrellaAssumptions()
    r = UmbrellaResult(day_rate=day_rate, assumptions=a)

    # Working pattern
    r.days_per_year = a.days_per_week * a.weeks_per_year
    r.hours_per_year = r.days_per_year * a.hours_per_day
    r.annual_gross_contract_income = day_rate * r.days_per_year

    # Step 1 — umbrella deductions
    r.umbrella_margin_annual = a.umbrella_margin_per_week * a.weeks_per_year
    gross_after_margin = r.annual_gross_contract_income - r.umbrella_margin_annual
    r.employer_ni = max(0, gross_after_margin - a.employer_ni_secondary_threshold) * a.employer_ni_rate
    r.apprenticeship_levy = gross_after_margin * a.apprenticeship_levy_rate
    r.gross_paye_salary = (
        r.annual_gross_contract_income
        - r.umbrella_margin_annual
        - r.employer_ni
        - r.apprenticeship_levy
    )

    # Qualifying earnings base for pension
    r.qualifying_earnings_base = max(
        0,
        min(r.gross_paye_salary, a.qualifying_earnings_upper) - a.qualifying_earnings_lower
    )

    # Employer pension (paid by umbrella on top of gross — does not reduce gross_paye_salary)
    r.employer_pension_annual = r.qualifying_earnings_base * a.employer_pension_rate

    # Step 2 — pre-tax pension deduction
    if a.pension_scheme_type in ("Net pay arrangement", "Salary sacrifice"):
        r.employee_pension_pretax = r.qualifying_earnings_base * a.employee_pension_rate
    else:
        r.employee_pension_pretax = 0

    r.gross_taxable_pay = r.gross_paye_salary - r.employee_pension_pretax

    # Step 3 — income tax
    r.taxable_income = max(0, r.gross_taxable_pay - a.personal_allowance)

    basic_band = max(0, a.basic_rate_ceiling - a.personal_allowance)
    higher_band = max(0, a.higher_rate_ceiling - a.basic_rate_ceiling)

    basic_taxable = min(r.taxable_income, basic_band)
    higher_taxable = min(max(0, r.taxable_income - basic_band), higher_band)
    additional_taxable = max(0, r.taxable_income - basic_band - higher_band)

    r.income_tax_basic = basic_taxable * a.income_tax_basic
    r.income_tax_higher = higher_taxable * a.income_tax_higher
    r.income_tax_additional = additional_taxable * a.income_tax_additional
    r.total_income_tax = r.income_tax_basic + r.income_tax_higher + r.income_tax_additional

    # Step 3 — employee NI
    ni_base = r.gross_taxable_pay  # pension already deducted if net pay / salary sacrifice
    standard_ni_base = min(max(0, ni_base - a.ni_primary_threshold), a.ni_upper_earnings_limit - a.ni_primary_threshold)
    above_uel_base = max(0, ni_base - a.ni_upper_earnings_limit)

    r.employee_ni_standard = standard_ni_base * a.ni_rate_standard
    r.employee_ni_above_uel = above_uel_base * a.ni_rate_above_uel
    r.total_employee_ni = r.employee_ni_standard + r.employee_ni_above_uel

    # Step 3b — post-tax deductions
    if a.pension_scheme_type == "Relief at source":
        r.employee_pension_posttax = r.qualifying_earnings_base * a.employee_pension_rate
        r.hmrc_basic_rate_topup = r.employee_pension_posttax * (a.income_tax_basic / (1 - a.income_tax_basic))
    else:
        r.employee_pension_posttax = 0
        r.hmrc_basic_rate_topup = 0

    if a.pension_scheme_type == "Salary sacrifice" and a.employer_passes_ni_saving_to_pension:
        sacrifice_amount = r.qualifying_earnings_base * a.employee_pension_rate
        r.employer_ni_saving_salary_sacrifice = sacrifice_amount * a.employer_ni_rate
        r.employer_ni_saving_to_pension = r.employer_ni_saving_salary_sacrifice
    else:
        r.employer_ni_saving_salary_sacrifice = 0
        r.employer_ni_saving_to_pension = 0

    r.total_pension_pot = (
        r.employee_pension_pretax
        + r.employee_pension_posttax
        + r.hmrc_basic_rate_topup
        + r.employer_ni_saving_to_pension
    )

    # Net take-home
    r.annual_net = r.gross_taxable_pay - r.total_income_tax - r.total_employee_ni - r.employee_pension_posttax
    r.monthly_net = r.annual_net / 12
    r.daily_net = r.annual_net / r.days_per_year
    r.hourly_net = r.annual_net / r.hours_per_year

    # Cost to client
    r.total_cost_to_client = r.annual_gross_contract_income + r.employer_pension_annual
    r.gross_salary_pct_of_client_cost = r.gross_paye_salary / r.total_cost_to_client

    # Effective rates & summary
    r.effective_tax_rate = 1 - (r.annual_net / r.annual_gross_contract_income)
    r.income_tax_paid = r.total_income_tax
    r.employee_ni_paid = r.total_employee_ni
    r.umbrella_margin_paid = r.umbrella_margin_annual
    r.employee_pension_contribution = r.employee_pension_pretax + r.employee_pension_posttax
    r.employer_pension_contribution = r.employer_pension_annual

    return r
