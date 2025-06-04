from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, or_, delete
from sqlalchemy.exc import NoResultFound

from app.db.session import AsyncSessionLocal
from app.models.match import Match
from app.schemas.match import MatchCreate, MatchRead, MatchUpdate
from datetime import datetime, timedelta
from app.models.judge import Judge

router = APIRouter(prefix="/matches", tags=["Matches"])
logger = logging.getLogger(__name__)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- Логика этапов турнира --------------------------------------------------

STAGE_ORDER = ["1/8", "1/4", "1/2", "финал", "3 место"]

def get_next_stage(current: str) -> str | None:
    try:
        idx = STAGE_ORDER.index(current)
        # "матч за 3 место" никогда не является next_stage
        if STAGE_ORDER[idx] == "финал":
            return None
        return STAGE_ORDER[idx + 1]
    except (ValueError, IndexError):
        return None

async def fill_next_stage_slot(db: AsyncSession, finished: Match):
    next_stage = get_next_stage(finished.stage)
    if not next_stage or next_stage == "3 место":
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
            if stub.red_participant_id is None:
                stub.red_participant_type = finished.winner_participant_type
                stub.red_participant_id   = finished.winner_participant_id
            else:
                stub.blue_participant_type = finished.winner_participant_type
                stub.blue_participant_id   = finished.winner_participant_id

# --- CRUD-эндпоинты ---------------------------------------------------------

@router.post("/", response_model=MatchRead)
async def create_match(match: MatchCreate, db: AsyncSession = Depends(get_db)):
    # --- Проверка: нельзя создавать матч за 3 место руками ---
    if match.stage == "3 место":
        raise HTTPException(status_code=400, detail="Матч за 3 место создаётся автоматически по итогам полуфиналов")
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
    # --- Проверка: не даём вручную создать матч за 3 место через batch ---
    for m in matches:
        if m.stage == "3 место":
            raise HTTPException(status_code=400, detail="Матч за 3 место создаётся автоматически по итогам полуфиналов")
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
    db_match = await db.get(Match, match_id)
    if not db_match:
        raise HTTPException(status_code=404, detail="Match not found")

    update_data = match_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    logger.info("PUT update_data: %s", update_data)

    await db.execute(
        update(Match)
        .where(Match.id == match_id)
        .values(**update_data)
    )
    await db.commit()

    updated = await db.get(Match, match_id)
    logger.info(
        "PUT OK: id=%s, status=%s, winner=%s/%s",
        updated.id,
        updated.status,
        updated.winner_participant_type,
        updated.winner_participant_id
    )

    if updated.status == "finished" and updated.winner_participant_id:
        await fill_next_stage_slot(db, updated)

    if updated.stage == "1/2":
        await try_create_bronze_match(db, updated)

    return updated

# --- Логика матча за 3 место ------------------------------------------------

async def try_create_bronze_match(db: AsyncSession, finished: Match):
    # 1. Находим все полуфиналы этой категории
    stmt = select(Match).where(
        Match.competition_id == finished.competition_id,
        Match.category == finished.category,
        Match.stage == "1/2",
        Match.status == "finished"
    ).order_by(Match.id)
    result = await db.execute(stmt)
    semifinals = result.scalars().all()
    if len(semifinals) < 2:
        return

    losers = []
    for m in semifinals:
        if m.red_participant_id and m.red_participant_id != m.winner_participant_id:
            losers.append({"type": m.red_participant_type, "id": m.red_participant_id})
        if m.blue_participant_id and m.blue_participant_id != m.winner_participant_id:
            losers.append({"type": m.blue_participant_type, "id": m.blue_participant_id})

    # Оставляем только уникальных
    unique_losers = []
    ids_seen = set()
    for l in losers:
        if l["id"] not in ids_seen:
            unique_losers.append(l)
            ids_seen.add(l["id"])
        if len(unique_losers) == 2:
            break

    if len(unique_losers) < 2:
        return

    # Чистим все невалидные (битые) матчи за 3 место для этой категории/турнира
    await db.execute(
        delete(Match).where(
            Match.competition_id == finished.competition_id,
            Match.category == finished.category,
            Match.stage == "3 место",
            or_(
                Match.red_participant_id == None,
                Match.blue_participant_id == None
            )
        )
    )
    # Проверяем — нет ли уже нормального бронзового матча
    stmt = select(Match).where(
        Match.competition_id == finished.competition_id,
        Match.category == finished.category,
        Match.stage == "3 место",
        Match.red_participant_id != None,
        Match.blue_participant_id != None
    )
    exists = await db.execute(stmt)
    if exists.scalars().first():
        return

    # Создаём матч за 3 место
    bronze_match = Match(
        competition_id=finished.competition_id,
        category=finished.category,
        stage="3 место",
        status="upcoming",
        red_participant_type=unique_losers[0]["type"],
        red_participant_id=unique_losers[0]["id"],
        blue_participant_type=unique_losers[1]["type"],
        blue_participant_id=unique_losers[1]["id"]
    )
    db.add(bronze_match)
    await db.commit()

async def auto_assign_officials_to_matches(
    db: AsyncSession, 
    competition_id: int, 
    start_time: datetime = None
):
    """Автоматически назначает судей, рефери, ковры и время на существующие матчи"""
    
    # Получаем все матчи без назначенных судей
    result = await db.execute(
        select(Match).where(
            Match.competition_id == competition_id,
            or_(Match.referee_id == None, Match.judge_id == None, Match.tatami == None)
        ).order_by(Match.id)
    )
    matches = result.scalars().all()
    
    if not matches:
        return {"message": "Нет матчей для назначения судей", "assigned": 0}
    
    # Получаем судей для этого соревнования
    judges_result = await db.execute(
        select(Judge).where(Judge.competition_id == competition_id)
    )
    judges = judges_result.scalars().all()
    
    if not judges:
        return {"message": "Нет судей для назначения. Сначала импортируйте судей на странице 'Судейская'", "assigned": 0}
    
    # Разделяем судей по категориям
    referees = [j for j in judges if j.category in ['Международная', 'Национальная']]
    regular_judges = [j for j in judges if j.category in ['Национальная', 'Региональная']]
    
    # Если рефери мало, добавляем из обычных судей
    if len(referees) < 2:
        referees.extend(regular_judges[:3])
    
    # Получаем доступные ковры из судей
    available_carpets = list(set(j.tatami for j in judges if j.tatami))
    if not available_carpets:
        available_carpets = [1, 2, 3, 4]  # По умолчанию
    
    # Исправляем время - убираем timezone
    if start_time:
        # Если пришло время с timezone, убираем его
        if start_time.tzinfo is not None:
            base_time = start_time.replace(tzinfo=None)
        else:
            base_time = start_time
    else:
        # Создаем naive datetime (без timezone)
        base_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Назначаем судей и время
    referee_counter = 0
    judge_counter = 0
    carpet_counter = 0
    
    assigned_count = 0
    
    # Обновляем каждый матч отдельно, чтобы избежать проблем с batch update
    for i, match in enumerate(matches):
        updates_made = False
        
        # Назначаем ковер если не назначен
        if not match.tatami:
            carpet_num = available_carpets[carpet_counter % len(available_carpets)]
            match.tatami = f"Ковер {carpet_num}"
            carpet_counter += 1
            updates_made = True
        
        # Назначаем рефери если не назначен
        if not match.referee_id and referees:
            referee = referees[referee_counter % len(referees)]
            match.referee_id = referee.id
            referee_counter += 1
            updates_made = True
        
        # Назначаем судью если не назначен
        if not match.judge_id and regular_judges:
            judge = regular_judges[judge_counter % len(regular_judges)]
            match.judge_id = judge.id
            judge_counter += 1
            updates_made = True
        
        # Назначаем время если не назначено
        if not match.match_time:
            time_offset = (i // len(available_carpets)) * 8  # 8 минут на матч
            # Создаем naive datetime без timezone
            match_time = base_time + timedelta(minutes=time_offset)
            match.match_time = match_time
            updates_made = True
        
        if updates_made:
            assigned_count += 1
    
    # Коммитим все изменения
    await db.commit()
    
    return {
        "message": f"Назначены судьи для {len(matches)} матчей",
        "total_matches": len(matches),
        "referees_available": len(referees),
        "judges_available": len(regular_judges),
        "carpets_available": len(available_carpets),
        "assigned": assigned_count
    }

# Эндпоинт автоназначения
@router.post("/auto-assign-officials/{competition_id}")
async def auto_assign_officials(
    competition_id: int,
    start_time: Optional[datetime] = Query(None, description="Время начала"),
    db: AsyncSession = Depends(get_db)
):
    """Автоматически назначает судей, рефери, ковры и время на существующие матчи"""
    try:
        result = await auto_assign_officials_to_matches(db, competition_id, start_time)
        return result
    except Exception as e:
        logger.error(f"Ошибка автоназначения: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Ошибка автоназначения: {str(e)}")