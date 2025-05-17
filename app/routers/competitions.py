from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.models.competition import Competition, Venue
from app.schemas.competition import CompetitionCreate, CompetitionRead, VenueCreate, VenueRead
from sqlalchemy.orm import joinedload
router = APIRouter(prefix="/competitions", tags=["Competitions"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=CompetitionRead)
async def create_competition(competition: CompetitionCreate, db: AsyncSession = Depends(get_db)):
    new_comp = Competition(**competition.dict())
    db.add(new_comp)
    await db.commit()

    # безопасно загружаем объект обратно, уже с venue и city
    result = await db.execute(
        select(Competition)
        .options(joinedload(Competition.venue).joinedload(Venue.city))
        .where(Competition.id == new_comp.id)
    )
    comp_with_venue = result.scalar_one()

    # добавляем city_name вручную, если нужно для схемы
    if comp_with_venue.venue and comp_with_venue.venue.city:
        comp_with_venue.venue.city_name = comp_with_venue.venue.city.name

    return comp_with_venue

@router.get("/", response_model=List[CompetitionRead])
async def get_all_competitions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Competition).options(joinedload(Competition.venue).joinedload(Venue.city))
    )
    competitions = result.scalars().all()

    for comp in competitions:
        if comp.venue and comp.venue.city:
            comp.venue.city_name = comp.venue.city.name  # ← вручную прокидываем

    return competitions

@router.post("/venues/", response_model=VenueRead)
async def create_venue(venue: VenueCreate, db: AsyncSession = Depends(get_db)):
    new_venue = Venue(**venue.dict())
    db.add(new_venue)
    await db.commit()
    await db.refresh(new_venue)
    return new_venue

@router.get("/venues/", response_model=List[VenueRead])
async def get_all_venues(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Venue).options(joinedload(Venue.city))
    )
    venues = result.scalars().all()

    for v in venues:
        v.city_name = v.city.name if v.city else None  # безопасно

    return venues
@router.delete("/{competition_id}")
async def delete_competition(competition_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Competition).where(Competition.id == competition_id))
    competition = result.scalar_one_or_none()

    if competition is None:
        raise HTTPException(status_code=404, detail="Competition not found")

    await db.delete(competition)
    await db.commit()

    return {"detail": "Competition deleted"}