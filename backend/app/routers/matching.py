from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.match import calculate_investor_match_score
from app.models.firm import Firm
from app.models.investor import Investor

router = APIRouter(tags=["matching"])


@router.get("/firms/{firm_id}/matching-investors")
def get_matching_investors(
    firm_id: UUID,
    user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Top 5 investors matching the signed-in firm (firm_id must be the caller's own id)."""
    if firm_id != user:
        raise HTTPException(status_code=403, detail="Forbidden")
    # Get the firm
    firm = db.query(Firm).filter(Firm.cognito_sub == firm_id).first()
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")

    # Get all investors and calculate match scores
    investors = db.query(Investor).all()
    matches = []

    for investor in investors:
        score = calculate_investor_match_score(investor, firm)

        matches.append({
            "investor": {
                "name": investor.name,
                "email": investor.email,
                "num_investments": investor.num_investments,
                "industry": investor.industry,
                "location": investor.location,
            },
            "match_score": score
        })

    # Sort by score descending
    matches.sort(key=lambda x: x["match_score"], reverse=True)

    return matches[:5]


@router.get("/investors/{investor_id}/matching-firms")
def get_matching_firms(
    investor_id: UUID,
    user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Top 5 firms matching the signed-in investor (investor_id must be the caller's own id)."""
    if investor_id != user:
        raise HTTPException(status_code=403, detail="Forbidden")
    # Get the investor
    # fetch investor by cognito_sub
    investor = db.query(Investor).filter(Investor.cognito_sub == investor_id).first()
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")

    # Get all firms and calculate match scores
    firms = db.query(Firm).all()
    matches = []

    for firm in firms:
        score = calculate_investor_match_score(investor, firm)

        matches.append({
            "firm": {
                "name": firm.name,
                "email": firm.email,
                "industry": firm.industry,
                "location": firm.location,
                "num_investments": firm.num_investments
            },
            "match_score": score
        })

    # Sort by score descending
    matches.sort(key=lambda x: x["match_score"], reverse=True)

    return matches[:5]
