from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RequestTypeBase(BaseModel):
    name: str


class RequestTypeCreate(RequestTypeBase):
    pass


class RequestTypeRead(RequestTypeBase):
    id: int

    class Config:
        from_attributes = True


class ApplicationBase(BaseModel):
    competition_id: int
    request_type_id: int
    team_id: int
    request_date: datetime


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationRead(ApplicationBase):
    id: int

    class Config:
        from_attributes = True


class ApplicationParticipantBase(BaseModel):
    application_id: int
    user_id: int
    status: Optional[str] = None


class ApplicationParticipantCreate(ApplicationParticipantBase):
    pass


class ApplicationParticipantRead(ApplicationParticipantBase):
    id: int

    class Config:
        from_attributes = True
