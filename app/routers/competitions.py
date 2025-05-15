from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.models.competition import Competition, Venue
from app.schemas.competition import CompetitionCreate, CompetitionRead, VenueCreate, VenueRead

router = APIRouter(prefix="/competitions", tags=["Competitions"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=CompetitionRead)
async def create_competition(competition: CompetitionCreate, db: AsyncSession = Depends(get_db)):
    new_comp = Competition(**competition.dict())
    db.add(new_comp)
    await db.commit()
    await db.refresh(new_comp)
    return new_comp

@router.get("/", response_model=List[CompetitionRead])
async def get_all_competitions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Competition))
    return result.scalars().all()

@router.post("/venues/", response_model=VenueRead)
async def create_venue(venue: VenueCreate, db: AsyncSession = Depends(get_db)):
    new_venue = Venue(**venue.dict())
    db.add(new_venue)
    await db.commit()
    await db.refresh(new_venue)
    return new_venue

@router.get("/venues/", response_model=List[VenueRead])
async def get_all_venues(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Venue))
    return result.scalars().all()
