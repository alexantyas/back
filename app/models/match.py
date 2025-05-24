from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)

    red_participant_type   = Column(String(20), nullable=False)
    red_participant_id     = Column(Integer, nullable=False)
    blue_participant_type  = Column(String(20), nullable=False)
    blue_participant_id    = Column(Integer, nullable=False)

    # Новые поля для турнирного брэкета
    stage                  = Column(String(50), nullable=True)   # например "1/16", "quarter"
    status                 = Column(String(20), nullable=True)   # "scheduled", "finished" и т.п.
    category = Column(String(20), nullable=False)
    winner_participant_type= Column(String(20), nullable=True)
    winner_participant_id  = Column(Integer, nullable=True)

    competition_id         = Column(
        Integer,
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False
    )
    
    comment                = Column(String, nullable=True)
    match_time             = Column(DateTime, nullable=True)
    score                  = Column(Integer, nullable=True)

    referee_id             = Column(Integer, ForeignKey("users.id"), nullable=True)
    judge_id               = Column(Integer, ForeignKey("users.id"), nullable=True)

    competition            = relationship("Competition", back_populates="matches")
