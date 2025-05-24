from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MatchBase(BaseModel):
    red_participant_type: str
    red_participant_id: int
    blue_participant_type: str
    blue_participant_id: int

    # Новые поля для брэкета
    stage: Optional[str] = None
    status: Optional[str] = None
    category: str
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

class MatchUpdate(BaseModel):
    red_participant_type: Optional[str] = None
    red_participant_id: Optional[int] = None
    blue_participant_type: Optional[str] = None
    blue_participant_id: Optional[int] = None

    stage: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    winner_participant_type: Optional[str] = None
    winner_participant_id: Optional[int] = None
    competition_id: Optional[int] = None
    referee_id: Optional[int] = None
    judge_id: Optional[int] = None
    match_time: Optional[datetime] = None
    score: Optional[int] = None
    comment: Optional[str] = None

class MatchRead(MatchBase):
    id: int

    model_config = {
        "from_attributes": True
    }
