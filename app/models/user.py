from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db.base import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class City(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    country_id = Column(Integer, ForeignKey("countries.id"))

class AdditionalInfo(Base):
    __tablename__ = "additional_info"
    id = Column(Integer, primary_key=True)
    height = Column(Integer)
    weight = Column(Integer)
    rank = Column(String)
    gender = Column(String)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    birth_date = Column(Date)
    login = Column(String, unique=True)
    password = Column(String)
    phone = Column(String)           # ← НОВОЕ
    email = Column(String)           # ← НОВОЕ
    organization = Column(String)    # ← НОВОЕ

    role_id = Column(Integer, ForeignKey("roles.id"))
    country_id = Column(Integer, ForeignKey("countries.id"))
    city_id = Column(Integer, ForeignKey("cities.id"))
    additional_info_id = Column(Integer, ForeignKey("additional_info.id"))

    role = relationship("Role")
    country = relationship("Country")
    city = relationship("City")
    additional_info = relationship("AdditionalInfo")

