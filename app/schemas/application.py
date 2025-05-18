from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

from app.schemas.user import UserRead   # ← импорт вложенного

# --- RequestType ---
class RequestTypeBase(BaseModel):
    name: str

class RequestTypeCreate(RequestTypeBase):
    pass

class RequestTypeRead(RequestTypeBase):
    id: int
    class Config:
        orm_mode = True


# --- Индивидуальный участник ---
class ApplicationIndividualParticipantBase(BaseModel):
    application_id: Optional[int] = None
    user_id: int
    status: Optional[str] = None

class ApplicationIndividualParticipantCreate(ApplicationIndividualParticipantBase):
    pass

class ApplicationIndividualParticipantRead(ApplicationIndividualParticipantBase):
    id: int
    class Config:
        orm_mode = True


# --- Командный участник ---
class ApplicationTeamParticipantBase(BaseModel):
    application_id: Optional[int] = None
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    weight: int
    birth_date: date
    country_id: int
    city_id: int
    status: Optional[str] = None

class ApplicationTeamParticipantCreate(ApplicationTeamParticipantBase):
    pass

class ApplicationTeamParticipantRead(ApplicationTeamParticipantBase):
    id: int
    class Config:
        orm_mode = True


# --- Заявка ---
class ApplicationBase(BaseModel):
    competition_id: int
    request_type_id: int
    team_id: Optional[int] = None
    user_id: Optional[int] = None           # ← новое поле
    request_date: datetime

class ApplicationCreate(ApplicationBase):
    team_participants: Optional[List[ApplicationTeamParticipantCreate]] = None
    individual_participants: Optional[List[ApplicationIndividualParticipantCreate]] = None

class ApplicationRead(ApplicationBase):
    id: int

    individual_participants: List[ApplicationIndividualParticipantRead] = []
    team_participants:       List[ApplicationTeamParticipantRead]       = []

    # ← вложенный пользователь (тренер)
    user: Optional[UserRead] = None

    class Config:
        orm_mode = True
