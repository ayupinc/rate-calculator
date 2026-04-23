"""
Ltd Co Rate Calculator — core calculation module.
Mirrors the logic in the 'Outside IR35 (Ltd Co)' sheet of rate_calculator_v10.xlsx.
All monetary values in GBP, annual unless noted.
"""

from dataclasses import dataclass, field


@dataclass
class LtdCoAssumptions:
    # Working pattern
    days_per_week: float = 5
    weeks_per_year: float = 46
    hours_per_day: float = 7.5

    # Ltd Co tax & NI (2024/25)
    director_salary: float = 12_570
    employer_ni_secondary_threshold: float = 9_100
    employer_ni_rate: float = 0.138
    corporation_tax_rate: float = 0.25
    dividend_allowance: float = 500
    dividend_basic_rate: float = 0.0875
    dividend_higher_rate: float = 0.3375
    basic_rate_band_upper: float = 50_270
    personal_allowance: float = 12_570

    # Business expenses (annual)
    professional_indemnity_per_year: float = 1_200
    relevant_life_insurance_per_month: float = 72
    critical_illness_per_month: float = 50
    accountancy_per_year: float = 1_800
    other_expenses_per_year: float = 1_000

    # Pension (kept separate — company contribution)
    employer_pension_per_month: float = 500


@dataclass
class LtdCoResult:
    # Inputs
    day_rate: float = 0
    assumptions: LtdCoAssumptions = field(default_factory=LtdCoAssumptions)

    # Working pattern
    days_per_year: float = 0
    hours_per_year: float = 0
    annual_gross_contract_income: float = 0

    # Step 1 — company-level deductions
    director_salary: float = 0
    employer_ni_on_salary: float = 0
    employer_pension_annual: float = 0
    professional_indemnity_annual: float = 0
    relevant_life_insurance_annual: float = 0
    critical_illness_annual: float = 0
    accountancy_annual: float = 0
    other_expenses_annual: float = 0
    taxable_profit: float = 0
    corporation_tax: float = 0
    distributable_profit: float = 0

    # Step 2 — personal income
    dividends_drawn: float = 0
    total_personal_income: float = 0

    # Step 3 — personal tax
    income_tax_on_salary: float = 0
    employee_ni_on_salary: float = 0
    dividend_allowance_tax_free: float = 0
    dividends_basic_rate_band: float = 0
    dividends_higher_rate_band: float = 0
    dividend_tax: float = 0
    net_dividends_after_tax: float = 0

    # Net take-home
    annual_net: float = 0
    monthly_net: float = 0
    daily_net: float = 0
    hourly_net: float = 0

    # Contractor protection
    critical_illness_after_tax_cost: float = 0

    # Effective rates
    effective_tax_rate: float = 0
    corporation_tax_paid: float = 0
    dividend_tax_paid: float = 0
    employer_ni_paid: float = 0
    total_pension: float = 0


def calculate(day_rate: float, assumptions: LtdCoAssumptions = None) -> LtdCoResult:
    a = assumptions or LtdCoAssumptions()
    r = LtdCoResult(day_rate=day_rate, assumptions=a)

    # Working pattern
    r.days_per_year = a.days_per_week * a.weeks_per_year
    r.hours_per_year = r.days_per_year * a.hours_per_day
    r.annual_gross_contract_income = day_rate * r.days_per_year

    # Step 1 — company-level deductions
    r.director_salary = a.director_salary
    r.employer_ni_on_salary = max(0, a.director_salary - a.employer_ni_secondary_threshold) * a.employer_ni_rate
    r.employer_pension_annual = a.employer_pension_per_month * 12
    r.professional_indemnity_annual = a.professional_indemnity_per_year
    r.relevant_life_insurance_annual = a.relevant_life_insurance_per_month * 12
    r.critical_illness_annual = a.critical_illness_per_month * 12
    r.accountancy_annual = a.accountancy_per_year
    r.other_expenses_annual = a.other_expenses_per_year

    r.taxable_profit = (
        r.annual_gross_contract_income
        - r.director_salary
        - r.employer_ni_on_salary
        - r.employer_pension_annual
        - r.professional_indemnity_annual
        - r.relevant_life_insurance_annual
        - r.critical_illness_annual
        - r.accountancy_annual
        - r.other_expenses_annual
    )
    r.corporation_tax = r.taxable_profit * a.corporation_tax_rate
    r.distributable_profit = r.taxable_profit - r.corporation_tax

    # Step 2 — personal income
    r.dividends_drawn = r.distributable_profit
    r.total_personal_income = r.director_salary + r.dividends_drawn

    # Step 3 — personal tax on salary
    r.income_tax_on_salary = 0  # salary at personal allowance
    r.employee_ni_on_salary = 0  # salary below NI primary threshold

    # Dividend tax
    r.dividend_allowance_tax_free = a.dividend_allowance

    # Basic rate space = ceiling minus salary minus allowance
    basic_rate_space = max(0, a.basic_rate_band_upper - a.director_salary - a.dividend_allowance)
    taxable_dividends = max(0, r.dividends_drawn - a.dividend_allowance)
    r.dividends_basic_rate_band = min(taxable_dividends, basic_rate_space)
    r.dividends_higher_rate_band = max(0, taxable_dividends - basic_rate_space - a.dividend_allowance)

    r.dividend_tax = (
        r.dividends_basic_rate_band * a.dividend_basic_rate
        + r.dividends_higher_rate_band * a.dividend_higher_rate
    )
    r.net_dividends_after_tax = r.dividends_drawn - r.dividend_tax

    # Net take-home
    r.annual_net = r.director_salary + r.net_dividends_after_tax
    r.monthly_net = r.annual_net / 12
    r.daily_net = r.annual_net / r.days_per_year
    r.hourly_net = r.annual_net / r.hours_per_year

    # Contractor protection
    r.critical_illness_after_tax_cost = r.critical_illness_annual * (1 - a.corporation_tax_rate)

    # Effective rates
    r.effective_tax_rate = 1 - (r.annual_net / r.annual_gross_contract_income)
    r.corporation_tax_paid = r.corporation_tax
    r.dividend_tax_paid = r.dividend_tax
    r.employer_ni_paid = r.employer_ni_on_salary
    r.total_pension = r.employer_pension_annual

    return r
