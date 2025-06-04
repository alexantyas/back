from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.session import get_db
from app.models.referee import Referee
from app.schemas.referee import RefereeCreate, RefereeRead

import pandas as pd
from io import BytesIO

router = APIRouter()

# 1. Получить всех рефери по id соревнования
@router.get("/referees/", response_model=List[RefereeRead])
async def get_referees(
    competition_id: int = Query(..., description="ID соревнования"),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Referee).where(Referee.competition_id == competition_id))
    referees = result.scalars().all()
    return referees

# 2. Добавить (bulk) рефери через список
@router.post("/referees/", response_model=List[RefereeRead])
async def create_referees(
    referees: List[RefereeCreate],
    db: AsyncSession = Depends(get_db)
):
    objs = [Referee(**r.dict()) for r in referees]
    db.add_all(objs)
    await db.commit()
    for obj in objs:
        await db.refresh(obj)
    return objs

# 3. Импортировать рефери через Excel-файл
@router.post("/referees/import/", response_model=dict)
async def import_referees(
    competition_id: int = Query(..., description="ID соревнования"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    content = await file.read()
    df = pd.read_excel(BytesIO(content))
    referees = []
    for _, row in df.iterrows():
        name = str(row.get("ФИО", "")).strip() or str(row.get("ФИО рефери", "")).strip()
        if not name:
            continue
        category = row.get("Квалификация") or None
        referee = Referee(
            name=name,
            category=category,
            competition_id=competition_id
        )
        referees.append(referee)
    if not referees:
        raise HTTPException(status_code=400, detail="В файле нет данных о рефери")
    db.add_all(referees)
    await db.commit()
    return {"added": len(referees)}

# 4. Удалить рефери (по id)
@router.delete("/referees/{referee_id}/", response_model=dict)
async def delete_referee(
    referee_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Referee).where(Referee.id == referee_id))
    referee = result.scalar_one_or_none()
    if not referee:
        raise HTTPException(status_code=404, detail="Referee not found")
    await db.delete(referee)
    await db.commit()
    return {"deleted": referee_id}