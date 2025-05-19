from datetime import datetime
from sqlalchemy import (
    Column,
    Date,
    Integer,
    String,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class RequestType(Base):
    __tablename__ = "request_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)


class Application(Base):
    __tablename__ = "applications"

    id            = Column(Integer, primary_key=True)
    request_date  = Column(DateTime, nullable=False, default=datetime.utcnow)

    competition_id = Column(Integer, ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)
    request_type_id = Column(
        Integer,
        ForeignKey("request_types.id"),
        nullable=False
    )
    team_id         = Column(
        Integer,
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True
    )
    user_id         = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # новое поле статуса
    status = Column(
        String(20),
        nullable=False,
        server_default="pending",  # в базе по умолчанию pending
        default="pending"          # в SQLAlchemy-объекте
    )

    # связи
    competition = relationship(
        "Competition",
        back_populates="applications",
        lazy="joined"
    )
    request_type = relationship("RequestType", lazy="joined")
    team         = relationship("Team", lazy="joined")
    user         = relationship("User", lazy="joined")

    individual_participants = relationship(
        "ApplicationIndividualParticipant",
        back_populates="application",
        cascade="all, delete-orphan",
    )
    team_participants = relationship(
        "ApplicationTeamParticipant",
        back_populates="application",
        cascade="all, delete-orphan",
    )


class ApplicationIndividualParticipant(Base):
    __tablename__ = "application_individual_participants"

    id             = Column(Integer, primary_key=True)
    application_id = Column(
        Integer,
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id        = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    # статус участника в заявке
    status = Column(
        String(20),
        nullable=False,
        server_default="pending",
        default="pending"
    )

    application = relationship(
        "Application",
        back_populates="individual_participants",
        lazy="joined",
    )
    user = relationship("User", lazy="joined")


class ApplicationTeamParticipant(Base):
    __tablename__ = "application_team_participants"

    id             = Column(Integer, primary_key=True)
    application_id = Column(
        Integer,
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False
    )

    first_name  = Column(String(100), nullable=False)
    last_name   = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    weight      = Column(Integer, nullable=False)
    birth_date  = Column(Date, nullable=False)
    country_id  = Column(Integer, nullable=False)
    city_id     = Column(Integer, nullable=False)
    # статус участника в командной заявке
    status = Column(
        String(20),
        nullable=False,
        server_default="pending",
        default="pending"
    )

    application = relationship(
        "Application",
        back_populates="team_participants",
        lazy="joined",
    )
