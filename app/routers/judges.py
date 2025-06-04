from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.session import AsyncSessionLocal
from app.models.judge import Judge
from app.schemas.judge import JudgeCreate, JudgeRead

import pandas as pd
from io import BytesIO

router = APIRouter()
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
# 1. Получить всех судей по id соревнования
@router.get("/judges/", response_model=List[JudgeRead])
async def get_judges(
    competition_id: int = Query(..., description="ID соревнования"),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Judge).where(Judge.competition_id == competition_id))
    judges = result.scalars().all()
    return judges

# 2. Добавить (bulk) судей через список
@router.post("/judges/", response_model=List[JudgeRead])
async def create_judges(
    judges: List[JudgeCreate],
    db: AsyncSession = Depends(get_db)
):
    objs = [Judge(**j.dict()) for j in judges]
    db.add_all(objs)
    await db.commit()
    for obj in objs:
        await db.refresh(obj)
    return objs

# 3. Импортировать судей через Excel-файл
@router.post("/judges/import/", response_model=dict)
async def import_judges(
    competition_id: int = Query(..., description="ID соревнования"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    content = await file.read()
    df = pd.read_excel(BytesIO(content))
    judges = []
    for _, row in df.iterrows():
        name = str(row.get("ФИО", "")).strip() or str(row.get("ФИО судьи", "")).strip()
        if not name:
            continue
        category = row.get("Квалификация") or None
        tatami = row.get("Ковер") or row.get("Татами") or 1
        judge = Judge(
            name=name,
            category=category,
            tatami=int(tatami) if not pd.isna(tatami) else 1,
            competition_id=competition_id
        )
        judges.append(judge)
    if not judges:
        raise HTTPException(status_code=400, detail="В файле нет данных о судьях")
    db.add_all(judges)
    await db.commit()
    return {"added": len(judges)}

# 4. Удалить судью (по id)
@router.delete("/judges/{judge_id}/", response_model=dict)
async def delete_judge(
    judge_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Judge).where(Judge.id == judge_id))
    judge = result.scalar_one_or_none()
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")
    await db.delete(judge)
    await db.commit()
    return {"deleted": judge_id}