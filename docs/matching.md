# How matching works

A match score compares one investor profile with one firm profile. The code is
[`backend/app/match.py`](../backend/app/match.py) (`calculate_investor_match_score`); the tests in
[`backend/tests/test_match.py`](../backend/tests/test_match.py) pin every row below, so this page and the code
cannot drift apart silently.

The score is **rule-based, not machine learning**. Gemini and Whisper are used only to fill in a firm's profile from a
recorded pitch (see [architecture](architecture.md)).

## The rules

Each criterion adds points independently. The maximum is **105**.

| Criterion | Points | How it scores |
| --- | --- | --- |
| Industry | 5 / 3 | 5 if equal (ignoring case); 3 if one contains the other (`Health` vs `HealthTech`) |
| Risk tolerance | 10 / 6 | 10 if equal; 6 if adjacent (Low-Medium, Medium-High); Low vs High scores 0 |
| Years active | 5 / 3 | 5 if the investor's years ≥ the firm's; 3 if at least half of it |
| Number of investments | 15 / 10 / 5 | Investor's count ≤ firm's: 15; ≤ 1.5× the firm's: 10; ≤ 2×: 5. A *lower* investor count scores higher, as implemented |
| Board seat | 10 | **Investor only**: 10 if the investor wants a board seat, whatever the firm says |
| Location | 10 | Exact match, ignoring case. `Toronto` vs `Toronto, ON` scores 0 |
| Investment size | 10 / 5 | Investor's size ≥ firm's: 10; at least half of it: 5 |
| Investment stage | 5 | Equal, ignoring case |
| Follow-on participation | 5 | **Investor only**: 5 if the investor does follow-ons |
| Rate of return | 10 / 5 | Investor's % ≥ firm's: 10; at least 80% of it: 5 (see the format note below) |
| Success rate | 5 | Investor's % ≥ firm's (see the format note below) |
| Reserved capital | 5 / 3 | Investor's amount ≥ firm's: 5; at least half of it: 3 (see the format note below) |
| Meeting frequency | 10 | Equal, ignoring case |

## Things that surprise people

- **Missing data scores nothing.** A criterion only counts when *both* profiles have a value, so a complete profile can
  score higher than an incomplete one. The exceptions are board seat and follow-on, which only look at the investor.
- **Value format matters for three fields.**
  - Rate of return and success rate need both sides to contain a `%` and parse as a bare number such as `18%`.
    `18% IRR` or `30% exits` score **0**.
  - Reserved capital needs a number with an optional `K`, `M` or `B` suffix, such as `5M` or `250K`.
    `40% fund reserved` scores **0**.
  - The investor form's placeholder examples (`18% IRR`, `30% exits`, `40% fund reserved`) are of the kind that score 0,
    and Gemini's free-form output for a firm can be too.
- **Scores are not percentages.** The maximum is 105, and the investor-side list shows the rounded score as is.

## What the API returns

- `GET /firms/{firm_id}/matching-investors` and `GET /investors/{investor_id}/matching-firms` score the caller
  against everyone on the other side, sort by score (highest first) and return the **top 5**.
- There is no minimum score: a 0 can appear when there are fewer than five profiles.
- The id in the URL must be the caller's own, or the API answers 403 (see [auth](auth.md)).
- The firm's list in the UI shows each investor's number of investments; the investor's list shows the match score.

## Changing the rules

Edit `calculate_investor_match_score`, update the table above and the matching tests together, and keep the
documented maximum in sync.
