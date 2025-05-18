from sqlalchemy import Column, Date, Integer, String, ForeignKey, DateTime
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

    competition_id    = Column(Integer, ForeignKey("competitions.id"))
    request_type_id   = Column(Integer, ForeignKey("request_types.id"))
    team_id           = Column(Integer, ForeignKey("teams.id"))
    user_id           = Column(Integer, ForeignKey("users.id"))       # ← новый

    competition       = relationship("Competition", back_populates="applications")
    request_type      = relationship("RequestType")
    team              = relationship("Team")
    user              = relationship("User")                           # ← связь на подающего

    individual_participants = relationship(
        "ApplicationIndividualParticipant",
        back_populates="application",
        cascade="all, delete-orphan"
    )
    team_participants       = relationship(
        "ApplicationTeamParticipant",
        back_populates="application",
        cascade="all, delete-orphan"
    )

class ApplicationIndividualParticipant(Base):
    __tablename__ = "application_individual_participants"
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    user_id        = Column(Integer, ForeignKey("users.id"))
    status         = Column(String)

    application = relationship("Application", back_populates="individual_participants")
    user        = relationship("User")

class ApplicationTeamParticipant(Base):
    __tablename__ = "application_team_participants"
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"))

    first_name  = Column(String)
    last_name   = Column(String)
    middle_name = Column(String)
    weight      = Column(Integer)
    birth_date  = Column(Date)
    country_id  = Column(Integer)
    city_id     = Column(Integer)
    status      = Column(String)

    application = relationship("Application", back_populates="team_participants")
