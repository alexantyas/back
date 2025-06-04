from pydantic import BaseModel

class JudgeBase(BaseModel):
    name: str
    category: str | None = None
    tatami: int | None = None

class JudgeCreate(JudgeBase):
    competition_id: int

class JudgeRead(JudgeBase):
    id: int
    competition_id: int

    class Config:
        from_attributes = True