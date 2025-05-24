from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.db.session import AsyncSessionLocal
from app.models.competition import Competition, Venue
from app.models.match import Match
from app.schemas.competition import CompetitionCreate, CompetitionRead, VenueCreate, VenueRead
from app.schemas.bracket import BracketRead, BracketUpdate
from app.schemas.match import MatchRead, MatchUpdate

router = APIRouter(prefix="/competitions", tags=["Competitions"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=CompetitionRead)
async def create_competition(
    competition: CompetitionCreate,
    db: AsyncSession = Depends(get_db)
):
    new_comp = Competition(**competition.dict())
    db.add(new_comp)
    await db.commit()

    # безопасно загружаем обратно с объединёнными Venue и City
    result = await db.execute(
        select(Competition)
        .options(joinedload(Competition.venue).joinedload(Venue.city))
        .where(Competition.id == new_comp.id)
    )
    comp_with_venue = result.scalar_one()

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
            comp.venue.city_name = comp.venue.city.name

    return competitions

@router.post("/venues/", response_model=VenueRead)
async def create_venue(
    venue: VenueCreate,
    db: AsyncSession = Depends(get_db)
):
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
        v.city_name = v.city.name if v.city else None

    return venues

# Новые эндпоинты для турнирной сетки (bracket)
@router.get("/{competition_id}/bracket", response_model=BracketRead)
async def get_bracket(
    competition_id: int,
    db: AsyncSession = Depends(get_db)
):
    # 1) Выбираем все матчи турнира
    result = await db.execute(
        select(Match).where(Match.competition_id == competition_id)
    )
    matches: List[Match] = result.scalars().all()
    # 2) Группируем по стадии
    rounds: Dict[str, List[MatchRead]] = {}
    for m in matches:
        key = m.stage or "unknown"
        rounds.setdefault(key, []).append(MatchRead.from_orm(m))
    return BracketRead(rounds=rounds)

@router.post("/{competition_id}/bracket", response_model=BracketRead)
async def post_bracket_results(
    competition_id: int,
    bracket: BracketUpdate,
    db: AsyncSession = Depends(get_db)
):
    # Массовое обновление матчей по этапам
    for stage_name, match_list in bracket.rounds.items():
        for mdata in match_list:
            db_match = await db.get(Match, mdata.id)
            if not db_match:
                raise HTTPException(status_code=404, detail=f"Match {mdata.id} not found")
            update_data = mdata.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_match, field, value)
            # Гарантируем, что стадия совпадает с ключом
            setattr(db_match, "stage", stage_name)
            db.add(db_match)
    await db.commit()
    # Возвращаем обновлённый брэкет
    return await get_bracket(competition_id, db)

@router.delete("/{competition_id}")
async def delete_competition(
    competition_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Competition).where(Competition.id == competition_id))
    competition = result.scalar_one_or_none()

    if competition is None:
        raise HTTPException(status_code=404, detail="Competition not found")

    await db.delete(competition)
    await db.commit()

    return {"detail": "Competition deleted"}