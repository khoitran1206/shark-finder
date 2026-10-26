from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.investor import Investor
from app.schemas import InvestorCreate

router = APIRouter()


@router.post("/investor/create-profile")
def create_investor(
    payload: InvestorCreate,
    sub: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_investor = Investor(**payload.dict(), cognito_sub=sub)
    db.add(new_investor)
    try:
        db.commit()
        db.refresh(new_investor)
        return new_investor
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Profile already exists for this user")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/investor/exists")
def investor_exists(
    sub: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exists = db.execute(
        select(Investor.cognito_sub).where(Investor.cognito_sub == sub)
    ).first() is not None
    return {"exists": exists}
