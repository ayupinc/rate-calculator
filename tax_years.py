"""
Tax year constants — rates and thresholds by year.
Sources: HMRC, House of Commons Library, GOV.UK published rates.

Key changes by year:
  2023/24 → 2024/25: Employee NI cut from 12% to 8% (staged: 10% from Jan 2024, 8% from Apr 2024).
                     Dividend allowance halved from £1,000 to £500.
  2024/25 → 2025/26: Employer NI rate up from 13.8% to 15%.
                     Employer NI secondary threshold down from £9,100 to £5,000.
  2025/26 → 2026/27: No changes to rates used in these calculators.
"""

TAX_YEARS = {
    "2026/27": {
        "label": "2026/27 (current)",
        "personal_allowance": 12_570,
        "basic_rate_ceiling": 50_270,
        "higher_rate_ceiling": 125_140,
        "income_tax_basic": 0.20,
        "income_tax_higher": 0.40,
        "income_tax_additional": 0.45,
        "ni_primary_threshold": 12_570,
        "ni_rate_standard": 0.08,
        "ni_upper_earnings_limit": 50_270,
        "ni_rate_above_uel": 0.02,
        "employer_ni_threshold": 5_000,
        "employer_ni_rate": 0.15,
        "dividend_allowance": 500,
        "dividend_basic_rate": 0.0875,
        "dividend_higher_rate": 0.3375,
        "corporation_tax_rate": 0.25,
        "notes": {
            "employer_ni_rate": "Increased from 13.8% to 15% in April 2025. Unchanged for 2026/27.",
            "employer_ni_threshold": "Dropped from £9,100 to £5,000 in April 2025. Unchanged for 2026/27.",
        },
    },
    "2025/26": {
        "label": "2025/26",
        "personal_allowance": 12_570,
        "basic_rate_ceiling": 50_270,
        "higher_rate_ceiling": 125_140,
        "income_tax_basic": 0.20,
        "income_tax_higher": 0.40,
        "income_tax_additional": 0.45,
        "ni_primary_threshold": 12_570,
        "ni_rate_standard": 0.08,
        "ni_upper_earnings_limit": 50_270,
        "ni_rate_above_uel": 0.02,
        "employer_ni_threshold": 5_000,
        "employer_ni_rate": 0.15,
        "dividend_allowance": 500,
        "dividend_basic_rate": 0.0875,
        "dividend_higher_rate": 0.3375,
        "corporation_tax_rate": 0.25,
        "notes": {
            "employer_ni_rate": "Increased from 13.8% to 15% from April 2025 (Autumn Budget 2024).",
            "employer_ni_threshold": "Dropped from £9,100 to £5,000 from April 2025 (Autumn Budget 2024).",
        },
    },
    "2024/25": {
        "label": "2024/25",
        "personal_allowance": 12_570,
        "basic_rate_ceiling": 50_270,
        "higher_rate_ceiling": 125_140,
        "income_tax_basic": 0.20,
        "income_tax_higher": 0.40,
        "income_tax_additional": 0.45,
        "ni_primary_threshold": 12_570,
        "ni_rate_standard": 0.08,
        "ni_upper_earnings_limit": 50_270,
        "ni_rate_above_uel": 0.02,
        "employer_ni_threshold": 9_100,
        "employer_ni_rate": 0.138,
        "dividend_allowance": 500,
        "dividend_basic_rate": 0.0875,
        "dividend_higher_rate": 0.3375,
        "corporation_tax_rate": 0.25,
        "notes": {},
    },
    "2023/24": {
        "label": "2023/24",
        "personal_allowance": 12_570,
        "basic_rate_ceiling": 50_270,
        "higher_rate_ceiling": 125_140,
        "income_tax_basic": 0.20,
        "income_tax_higher": 0.40,
        "income_tax_additional": 0.45,
        "ni_primary_threshold": 12_570,
        "ni_rate_standard": 0.12,
        "ni_upper_earnings_limit": 50_270,
        "ni_rate_above_uel": 0.02,
        "employer_ni_threshold": 9_100,
        "employer_ni_rate": 0.138,
        "dividend_allowance": 1_000,
        "dividend_basic_rate": 0.0875,
        "dividend_higher_rate": 0.3375,
        "corporation_tax_rate": 0.25,
        "notes": {
            "ni_rate_standard": "Rate was 12% from April 2023, cut to 10% from January 2024, then 8% from April 2024. This calculator uses the April 2023 opening rate of 12% for the full year.",
            "dividend_allowance": "Allowance was £1,000 (halved from £2,000 in 2022/23, halved again to £500 from 2024/25).",
        },
    },
}

TAX_YEAR_OPTIONS = list(TAX_YEARS.keys())
DEFAULT_TAX_YEAR = "2026/27"
