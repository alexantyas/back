from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VenueBase(BaseModel):
    name: str
    city_id: int

class VenueCreate(VenueBase):
    pass

class VenueRead(BaseModel):
    id: int
    name: str
    city_id: int
    city_name: Optional[str] = None

    class Config:
        from_attributes = True

class CompetitionBase(BaseModel):
    name: str
    organizer: str
    start_date: datetime
    status: Optional[str] = None
    comment: Optional[str] = None
    venue_id: int

class CompetitionCreate(CompetitionBase):
    pass

class CompetitionRead(CompetitionBase):
    id: int
    venue: Optional[VenueRead]

    class Config:
        from_attributes = True