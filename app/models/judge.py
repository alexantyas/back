from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base

class Judge(Base):
    __tablename__ = "judges"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String)
    tatami = Column(Integer)
    competition_id = Column(Integer, ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)