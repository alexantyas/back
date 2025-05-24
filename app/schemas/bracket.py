from typing import Dict, List
from pydantic import BaseModel
from .match import MatchRead, MatchUpdate

class BracketRead(BaseModel):
    # «rounds»: имя раунда → список матчей
    rounds: Dict[str, List[MatchRead]]

class BracketUpdate(BaseModel):
    # приходит такой же словарь, но с частичной моделью MatchUpdate
    rounds: Dict[str, List[MatchUpdate]]