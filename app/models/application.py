from sqlalchemy import Column, Integer, String, ForeignKey, DateTime  # ← добавь DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

from sqlalchemy.orm import relationship
from app.db.base import Base

class RequestType(Base):
    __tablename__ = "request_types"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    request_date = Column(DateTime)
    
    competition_id = Column(Integer, ForeignKey("competitions.id"))
    request_type_id = Column(Integer, ForeignKey("request_types.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))

    competition = relationship("Competition", back_populates="applications")
    request_type = relationship("RequestType")
    team = relationship("Team")
    participants = relationship("ApplicationParticipant", back_populates="application")

class ApplicationParticipant(Base):
    __tablename__ = "application_participants"
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String)

    application = relationship("Application", back_populates="participants")
    user = relationship("User")
