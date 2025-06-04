from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base

class Referee(Base):
    __tablename__ = "referees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String)
    competition_id = Column(Integer, ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)