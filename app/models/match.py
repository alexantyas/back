from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)

    red_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    blue_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    winner_id = Column(Integer, ForeignKey("users.id"))
    competition_id = Column(Integer, ForeignKey("competitions.id"))

    comment = Column(String)
    match_time = Column(DateTime)
    score = Column(Integer)
    referee_id = Column(Integer, ForeignKey("users.id"))
    judge_id = Column(Integer, ForeignKey("users.id"))

    red = relationship("User", foreign_keys=[red_id])
    blue = relationship("User", foreign_keys=[blue_id])
    winner = relationship("User", foreign_keys=[winner_id])
    referee = relationship("User", foreign_keys=[referee_id])
    judge = relationship("User", foreign_keys=[judge_id])

    competition = relationship("Competition", back_populates="matches")
