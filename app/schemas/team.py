from pydantic import BaseModel


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
    user_id: int


class TeamMemberCreate(TeamMemberBase):
    pass


class TeamMemberRead(TeamMemberBase):
    id: int

    class Config:
        from_attributes = True
