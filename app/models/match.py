from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)

    red_participant_type   = Column(String(20), nullable=False)
    red_participant_id     = Column(Integer, nullable=False)
    blue_participant_type  = Column(String(20), nullable=True)
    blue_participant_id    = Column(Integer, nullable=True)

    stage                  = Column(String(50), nullable=True)
    status                 = Column(String(20), nullable=True)
    category               = Column(String(20), nullable=False)
    winner_participant_type= Column(String(20), nullable=True)
    winner_participant_id  = Column(Integer, nullable=True)

    competition_id         = Column(Integer, ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)
    comment                = Column(String, nullable=True)
    match_time             = Column(DateTime, nullable=True)
    score                  = Column(Integer, nullable=True)
    tatami                 = Column(String(50), nullable=True)
    
    # ИСПРАВЛЕННЫЕ связи - теперь ссылаются на таблицу judges
    referee_id             = Column(Integer, ForeignKey("judges.id"), nullable=True)  # ← Исправлено!
    judge_id               = Column(Integer, ForeignKey("judges.id"), nullable=True)   # ← Исправлено!
    
    # Связи
    competition            = relationship("Competition", back_populates="matches")
    referee                = relationship("Judge", foreign_keys=[referee_id])         # ← Добавлено
    judge                  = relationship("Judge", foreign_keys=[judge_id])           # ← Добавлено