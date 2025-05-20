from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MatchBase(BaseModel):
    red_participant_type: str  # "individual" или "team"
    red_participant_id: int
    blue_participant_type: str
    blue_participant_id: int
    winner_participant_type: Optional[str] = None
    winner_participant_id: Optional[int] = None
    competition_id: int
    referee_id: Optional[int] = None
    judge_id: Optional[int] = None
    match_time: Optional[datetime] = None
    score: Optional[int] = None
    comment: Optional[str] = None

class MatchCreate(MatchBase):
    pass

class MatchRead(MatchBase):
    id: int

    class Config:
        orm_mode = True