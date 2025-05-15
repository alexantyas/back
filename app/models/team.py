from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    coach_id = Column(Integer, ForeignKey("users.id"))

    coach = relationship("User", backref="coached_teams")
    members = relationship("TeamMember", back_populates="team")

class TeamMember(Base):
    __tablename__ = "team_members"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    team = relationship("Team", back_populates="members")
    user = relationship("User")
