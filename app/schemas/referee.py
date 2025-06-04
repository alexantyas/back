from pydantic import BaseModel

class RefereeBase(BaseModel):
    name: str
    category: str | None = None

class RefereeCreate(RefereeBase):
    competition_id: int

class RefereeRead(RefereeBase):
    id: int
    competition_id: int

    class Config:
        from_attributes = True