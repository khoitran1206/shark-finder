from typing import Literal, Optional

from pydantic import BaseModel, EmailStr


class InvestorCreate(BaseModel):
    name: str
    email: EmailStr
    risk_tolerance: Optional[Literal["Low", "Medium", "High"]] = None
    industry: Optional[str] = None
    years_active: Optional[int] = None
    num_investments: Optional[int] = None
    board_seat: Optional[bool] = None
    location: Optional[str] = None
    investment_size: Optional[int] = None
    investment_stage: Optional[Literal["Pre-seed", "Seed", "Series A", "Series B+", "Public"]] = None
    follow_on_rate: Optional[bool] = None
    rate_of_return: Optional[str] = None
    success_rate: Optional[str] = None
    reserved_capital: Optional[str] = None
    meeting_frequency: Optional[Literal["Weekly", "Monthly", "Quarterly"]] = None
