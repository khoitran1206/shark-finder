from app.models.firm import Firm
from app.models.investor import Investor


def calculate_investor_match_score(investor: Investor, firm: Firm) -> float:
    """Score how well an investor matches a firm (higher is better, max 105)."""
    score = 0.0

    # Industry match (up to 5 points)
    if investor.industry and firm.industry:
        if investor.industry.lower() == firm.industry.lower():
            score += 5
        elif investor.industry.lower() in firm.industry.lower() or firm.industry.lower() in investor.industry.lower():
            score += 3

    # Risk tolerance (up to 10 points; adjacent levels get 6)
    if investor.risk_tolerance and firm.risk_tolerance:
        inv_risk = investor.risk_tolerance.lower()
        firm_risk = firm.risk_tolerance.lower()
        if inv_risk == firm_risk:
            score += 10
        elif {inv_risk, firm_risk} in ({'low', 'medium'}, {'medium', 'high'}):
            score += 6

    # Experience level (up to 5 points)
    if investor.years_active and firm.years_active:
        if investor.years_active >= firm.years_active:
            score += 5
        elif investor.years_active >= firm.years_active * 0.5:
            score += 3

    # Number of investments vs firm's (up to 15 points)
    if investor.num_investments and firm.num_investments:
        if investor.num_investments <= firm.num_investments:
            score += 15
        elif investor.num_investments <= firm.num_investments * 1.5:
            score += 10
        elif investor.num_investments <= firm.num_investments * 2:
            score += 5

    # Board seat preference (10 points)
    if investor.board_seat:
        score += 10


    # Location match (10 points)
    if investor.location and firm.location:
        if investor.location.lower() == firm.location.lower():
            score += 10


    # Investment size (up to 10 points)
    if investor.investment_size and firm.investment_size:
        if investor.investment_size >= firm.investment_size:
            score += 10
        elif investor.investment_size >= firm.investment_size * 0.5:
            score += 5

    # Investment stage (5 points)
    if investor.investment_stage and firm.investment_stage:
        if investor.investment_stage.lower() == firm.investment_stage.lower():
            score += 5


    # Follow-on preference (5 points)
    if investor.follow_on_rate:
        score += 5

    # Rate of return (up to 10 points)
    if investor.rate_of_return and firm.rate_of_return:
        # small bonus for higher stated ROI strings (heuristic)
        if '%' in investor.rate_of_return and '%' in firm.rate_of_return:
            try:
                investor_roi = float(investor.rate_of_return.replace('%',''))
                firm_roi = float(firm.rate_of_return.replace('%',''))
                if investor_roi >= firm_roi:
                    score += 10
                elif investor_roi >= firm_roi * 0.8:
                    score += 5
            except:
                pass

    # Success rate (5 points)
    if investor.success_rate and firm.success_rate:
        # small bonus for higher stated success rate strings (heuristic)
        if '%' in investor.success_rate and '%' in firm.success_rate:
            try:
                investor_sr = float(investor.success_rate.replace('%',''))
                firm_sr = float(firm.success_rate.replace('%',''))
                if investor_sr >= firm_sr:
                    score += 5
            except:
                pass


    # Reserved capital (up to 5 points)
    if investor.reserved_capital and firm.reserved_capital:
        try:
            inv_cap = parse_amount(investor.reserved_capital) if isinstance(investor.reserved_capital, str) else float(investor.reserved_capital)
            firm_cap = parse_amount(firm.reserved_capital) if isinstance(firm.reserved_capital, str) else float(firm.reserved_capital)
            if inv_cap >= firm_cap:
                score += 5
            elif inv_cap >= firm_cap * 0.5:
                score += 3
        except:
            pass


    # Meeting frequency (10 points)
    if investor.meeting_frequency and firm.meeting_frequency:
        if investor.meeting_frequency.lower() == firm.meeting_frequency.lower():
            score += 10


    return score


def parse_amount(amount_str: str) -> float:
    """Parse amounts like '100M', '1.5B', etc."""
    amount_str = amount_str.upper().strip()
    multipliers = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000}

    for suffix, multiplier in multipliers.items():
        if suffix in amount_str:
            number = float(amount_str.replace(suffix, '').strip())
            return number * multiplier

    return float(amount_str)


def format_amount(amount: float) -> str:
    """Format amount as readable string."""
    if amount >= 1_000_000_000:
        return f"{amount / 1_000_000_000:.1f}B"
    elif amount >= 1_000_000:
        return f"{amount / 1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"{amount / 1_000:.1f}K"
    return f"{amount:.0f}"
