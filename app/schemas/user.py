from pydantic import BaseModel
from typing import Optional
from datetime import date

class UserBase(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    login: str
    phone: Optional[str] = None        # ← НОВОЕ
    email: Optional[str] = None        # ← НОВОЕ
    organization: Optional[str] = None # ← НОВОЕ


class UserCreate(UserBase):
    birth_date: date  
    password: str
    role_id: int
    country_id: int
    city_id: int
    additional_info_id: int


class UserRead(UserBase):
    id: int
    role_id: int
    city_id: int
    country_id: int

    class Config:
        from_attributes = True

class UserCreateFrontend(BaseModel):
    fullName: str
    birthDate: date
    city: str
    country: str
    phone: str
    email: str
    organization: str
    username: str
    password: str
    role: str = "coach"

class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

class AdditionalInfoBase(BaseModel):
    height: Optional[int] = None
    weight: Optional[int] = None
    rank: Optional[str] = None
    gender: Optional[str] = None

class AdditionalInfoCreate(AdditionalInfoBase):
    pass

class AdditionalInfoRead(AdditionalInfoBase):
    id: int

    class Config:
        from_attributes = True