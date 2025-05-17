from pydantic import BaseModel
from typing import Optional
from datetime import date

class TeamBase(BaseModel):
    name: str
    coach_id: int

class TeamCreate(TeamBase):
    pass

class TeamRead(TeamBase):
    id: int
    class Config:
        from_attributes = True

class TeamMemberBase(BaseModel):
    team_id: int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    weight: int
    birth_date: date
    country_id: int
    city_id: int

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMemberRead(TeamMemberBase):
    id: int
    class Config:
        from_attributes = True
