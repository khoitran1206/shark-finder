from types import SimpleNamespace

import pytest

from app.match import calculate_investor_match_score

FIELDS = [
    "industry", "risk_tolerance", "years_active", "num_investments", "board_seat",
    "location", "investment_size", "investment_stage", "follow_on_rate",
    "rate_of_return", "success_rate", "reserved_capital", "meeting_frequency",
]


def party(**kwargs):
    return SimpleNamespace(**{f: kwargs.get(f) for f in FIELDS})


def test_empty_profiles_score_zero():
    assert calculate_investor_match_score(party(), party()) == 0


@pytest.mark.parametrize(
    "investor_risk, firm_risk, expected",
    [
        ("Medium", "Medium", 10),
        ("medium", "Medium", 10),
        ("Low", "Medium", 6),
        ("Medium", "Low", 6),
        ("High", "Medium", 6),
        ("Medium", "High", 6),
        ("Low", "High", 0),
        ("High", "Low", 0),
    ],
)
def test_risk_tolerance_scoring_is_case_insensitive(investor_risk, firm_risk, expected):
    score = calculate_investor_match_score(
        party(risk_tolerance=investor_risk), party(risk_tolerance=firm_risk)
    )
    assert score == expected


def test_industry_exact_and_partial_match():
    assert calculate_investor_match_score(party(industry="Fintech"), party(industry="fintech")) == 5
    assert calculate_investor_match_score(party(industry="Fintech"), party(industry="Fintech Lending")) == 3
    assert calculate_investor_match_score(party(industry="Fintech"), party(industry="Biotech")) == 0


# Each row is one line of the table in docs/matching.md: (field, investor value, firm value, points).
DOCUMENTED_RULES = [
    ("industry", "Fintech", "fintech", 5),
    ("industry", "Health", "HealthTech", 3),
    ("years_active", 10, 5, 5),
    ("years_active", 3, 5, 3),
    ("years_active", 2, 5, 0),
    ("num_investments", 5, 10, 15),
    ("num_investments", 14, 10, 10),
    ("num_investments", 18, 10, 5),
    ("num_investments", 25, 10, 0),
    ("location", "Toronto", "toronto", 10),
    ("location", "Toronto", "Toronto, ON", 0),
    ("investment_size", 500_000, 250_000, 10),
    ("investment_size", 150_000, 250_000, 5),
    ("investment_size", 100_000, 250_000, 0),
    ("investment_stage", "seed", "Seed", 5),
    ("investment_stage", "Seed", "Series A", 0),
    ("rate_of_return", "18%", "15%", 10),
    ("rate_of_return", "12%", "15%", 5),
    ("rate_of_return", "10%", "15%", 0),
    ("rate_of_return", "18% IRR", "15% IRR", 0),  # format note: needs a bare number
    ("success_rate", "30%", "20%", 5),
    ("success_rate", "10%", "20%", 0),
    ("success_rate", "30% exits", "20% exits", 0),  # format note
    ("reserved_capital", "5M", "2M", 5),
    ("reserved_capital", "1M", "2M", 3),
    ("reserved_capital", "500K", "2M", 0),
    ("reserved_capital", "40% fund reserved", "40% fund reserved", 0),  # format note
    ("meeting_frequency", "monthly", "Monthly", 10),
    ("meeting_frequency", "Weekly", "Monthly", 0),
]


@pytest.mark.parametrize("field, investor_value, firm_value, points", DOCUMENTED_RULES)
def test_documented_scoring_rules(field, investor_value, firm_value, points):
    score = calculate_investor_match_score(party(**{field: investor_value}), party(**{field: firm_value}))
    assert score == points


def test_board_seat_and_follow_on_look_at_the_investor_only():
    assert calculate_investor_match_score(party(board_seat=True), party()) == 10
    assert calculate_investor_match_score(party(follow_on_rate=True), party()) == 5
    assert calculate_investor_match_score(party(), party(board_seat=True, follow_on_rate=True)) == 0


def test_a_criterion_needs_both_sides():
    assert calculate_investor_match_score(party(industry="Fintech", location="Toronto"), party()) == 0


def test_maximum_score_is_105():
    investor = party(
        industry="Fintech", risk_tolerance="Low", years_active=9, num_investments=1, board_seat=True,
        location="Toronto", investment_size=9, investment_stage="Seed", follow_on_rate=True,
        rate_of_return="9%", success_rate="9%", reserved_capital="9M", meeting_frequency="Weekly",
    )
    firm = party(
        industry="Fintech", risk_tolerance="Low", years_active=1, num_investments=5,
        location="Toronto", investment_size=1, investment_stage="Seed",
        rate_of_return="1%", success_rate="1%", reserved_capital="1M", meeting_frequency="Weekly",
    )
    assert calculate_investor_match_score(investor, firm) == 105
