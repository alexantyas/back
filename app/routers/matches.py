from fastapi import APIRouter, Depends, HTTPException
from typing import List
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, or_
from sqlalchemy.exc import NoResultFound

from app.db.session import AsyncSessionLocal
from app.models.match import Match
from app.schemas.match import MatchCreate, MatchRead, MatchUpdate

router = APIRouter(prefix="/matches", tags=["Matches"])
logger = logging.getLogger(__name__)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- Логика этапов турнира --------------------------------------------------

STAGE_ORDER = ["1/8 финала", "1/4 финала", "1/2 финала", "финал"]

def get_next_stage(current: str) -> str | None:
    try:
        idx = STAGE_ORDER.index(current)
        return STAGE_ORDER[idx + 1]
    except (ValueError, IndexError):
        return None

async def fill_next_stage_slot(db: AsyncSession, finished: Match):
    """
    Вносит в таблицу matches победителя в следующий этап.
    Если на этапе ещё нет «заготовки» (stub) – создаёт; иначе заполняет пустой слот.
    С конкурентным контролем через FOR UPDATE SKIP LOCKED.
    """
    next_stage = get_next_stage(finished.stage)
    if not next_stage:
        return

    async with db.begin():
        stmt = (
            select(Match)
            .where(
                Match.competition_id == finished.competition_id,
                Match.category       == finished.category,
                Match.stage          == next_stage,
                Match.status         == "upcoming",
                or_(
                    Match.red_participant_id  == None,
                    Match.blue_participant_id == None,
                )
            )
            .with_for_update(skip_locked=True)
            .order_by(Match.id)
            .limit(1)
        )
        result = await db.execute(stmt)
        try:
            stub: Match = result.scalar_one()
        except NoResultFound:
            stub = None

        if not stub:
            # создаём новый stub-матч с первым победителем
            stub = Match(
                competition_id           = finished.competition_id,
                category                 = finished.category,
                stage                    = next_stage,
                status                   = "upcoming",
                red_participant_type     = finished.winner_participant_type,
                red_participant_id       = finished.winner_participant_id
            )
            db.add(stub)
        else:
            # заполняем второй слот
            if stub.red_participant_id is None:
                stub.red_participant_type = finished.winner_participant_type
                stub.red_participant_id   = finished.winner_participant_id
            else:
                stub.blue_participant_type = finished.winner_participant_type
                stub.blue_participant_id   = finished.winner_participant_id

# --- CRUD-эндпоинты ---------------------------------------------------------

@router.post("/", response_model=MatchRead)
async def create_match(match: MatchCreate, db: AsyncSession = Depends(get_db)):
    new_match = Match(**match.model_dump())
    db.add(new_match)
    await db.commit()
    await db.refresh(new_match)
    return new_match

@router.post("/batch", response_model=List[MatchRead])
async def create_matches_batch(
    matches: List[MatchCreate],
    db: AsyncSession = Depends(get_db)
):
    new = [Match(**m.model_dump()) for m in matches]
    db.add_all(new)
    await db.commit()
    for m in new:
        await db.refresh(m)
    return new

@router.get("/", response_model=List[MatchRead])
async def get_all_matches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match))
    return result.scalars().all()

@router.get("/{match_id}", response_model=MatchRead)
async def get_match(match_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@router.put("/{match_id}", response_model=MatchRead)
async def put_match(
    match_id: int,
    match_update: MatchUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    PUT /matches/{match_id} —
    Обновляет указанные поля матча, сохраняет победителя и
    автоматически создаёт или дополняет матч следующего этапа.
    """
    # 1. Находим матч
    db_match = await db.get(Match, match_id)
    if not db_match:
        raise HTTPException(status_code=404, detail="Match not found")

    # 2. Собираем только переданные поля
    update_data = match_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    logger.info("PUT update_data: %s", update_data)

    # 3. Явный UPDATE через core-выражение
    await db.execute(
        update(Match)
        .where(Match.id == match_id)
        .values(**update_data)
    )
    await db.commit()

    # 4. Получаем обновлённый матч
    updated = await db.get(Match, match_id)
    logger.info(
        "PUT OK: id=%s, status=%s, winner=%s/%s",
        updated.id,
        updated.status,
        updated.winner_participant_type,
        updated.winner_participant_id
    )

    # 5. Если матч завершён и есть победитель — формируем следующий этап
    if updated.status == "finished" and updated.winner_participant_id:
        await fill_next_stage_slot(db, updated)

    return updated
