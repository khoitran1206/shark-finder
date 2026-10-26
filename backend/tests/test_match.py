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
