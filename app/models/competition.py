from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Venue(Base):
    __tablename__ = "venues"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    city_id = Column(Integer, ForeignKey("cities.id"))

    city = relationship("City")

class Competition(Base):
    __tablename__ = "competitions"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    organizer = Column(String)
    start_date = Column(DateTime)
    comment = Column(String)
    venue_id = Column(Integer, ForeignKey("venues.id"))
    status = Column(String)

    venue = relationship("Venue")
    applications = relationship("Application", back_populates="competition")
    matches = relationship("Match", back_populates="competition")
