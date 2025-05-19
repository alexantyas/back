from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MatchBase(BaseModel):
    red_id: Optional[int] = None
    blue_id: Optional[int] = None
    winner_id: Optional[int] = None
    competition_id:int
    referee_id:    Optional[int] = None
    judge_id:      Optional[int] = None
    match_time:    Optional[datetime] = None
    score:         Optional[int] = None
    comment:       Optional[str] = None


class MatchCreate(MatchBase):
    pass


class MatchRead(MatchBase):
    id: int

    class Config:
        from_attributes = True
