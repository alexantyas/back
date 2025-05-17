# schemas/location.py
from pydantic import BaseModel

class CityRead(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class CountryRead(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True
