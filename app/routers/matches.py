from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.models.match import Match
from app.schemas.match import MatchCreate, MatchRead

router = APIRouter(prefix="/matches", tags=["Matches"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=MatchRead)
async def create_match(match: MatchCreate, db: AsyncSession = Depends(get_db)):
    new_match = Match(**match.dict())
    db.add(new_match)
    await db.commit()
    await db.refresh(new_match)
    return new_match

@router.get("/", response_model=List[MatchRead])
async def get_all_matches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match))
    return result.scalars().all()

@router.get("/{match_id}", response_model=MatchRead)
async def get_match(match_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return match
@router.post("/batch", response_model=List[MatchRead])
async def create_matches_batch(
    matches: List[MatchCreate], 
    db: AsyncSession = Depends(get_db)
):
    new = [Match(**m.dict()) for m in matches]
    db.add_all(new)
    await db.commit()
    for m in new: await db.refresh(m)
    return new