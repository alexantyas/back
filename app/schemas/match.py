from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Для создания (POST)
class MatchCreate(BaseModel):
    red_participant_type: str
    red_participant_id: int
    blue_participant_type: str
    blue_participant_id: int
    competition_id: int
    category: str

    stage: Optional[str] = None
    status: Optional[str] = None
    referee_id: Optional[int] = None
    judge_id: Optional[int] = None
    match_time: Optional[datetime] = None
    score: Optional[int] = None
    comment: Optional[str] = None
    winner_participant_type: Optional[str] = None
    winner_participant_id: Optional[int] = None
    tatami: Optional[str] = None
    model_config = {
        "from_attributes": True
    }


# Для вывода (GET, PATCH response)
class MatchRead(BaseModel):
    id: int
    competition_id: int
    category: str

    red_participant_type: str
    red_participant_id: int
    blue_participant_type: Optional[str] = None    # теперь nullable
    blue_participant_id: Optional[int] = None      # теперь nullable

    stage: Optional[str] = None
    status: Optional[str] = None

    referee_id: Optional[int] = None
    judge_id: Optional[int] = None
    match_time: Optional[datetime] = None
    score: Optional[int] = None
    comment: Optional[str] = None

    winner_participant_type: Optional[str] = None
    winner_participant_id: Optional[int] = None
    tatami: Optional[str] = None
    model_config = {
        "from_attributes": True
    }


# Для обновления (PATCH)
class MatchUpdate(BaseModel):
    # можно менять только эти поля
    stage: Optional[str] = None
    status: Optional[str] = None
    match_time: Optional[datetime] = None
    judge_id: Optional[int] = None
    referee_id: Optional[int] = None
    score: Optional[int] = None
    comment: Optional[str] = None

    # специально оставляем для финального статуса
    winner_participant_type: Optional[str] = None
    winner_participant_id: Optional[int] = None
    tatami: Optional[str] = None
    model_config = {
        "from_attributes": True
    }
