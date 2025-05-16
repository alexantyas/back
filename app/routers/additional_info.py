from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.models.user import AdditionalInfo
from app.schemas.user import AdditionalInfoCreate, AdditionalInfoRead

router = APIRouter(prefix="/additional-info", tags=["AdditionalInfo"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=AdditionalInfoRead)
async def create_additional_info(
    additional_info: AdditionalInfoCreate,
    db: AsyncSession = Depends(get_db)
):
    new_info = AdditionalInfo(**additional_info.dict())
    db.add(new_info)
    await db.commit()
    await db.refresh(new_info)
    return new_info

@router.get("/{info_id}", response_model=AdditionalInfoRead)
async def get_additional_info(info_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AdditionalInfo).where(AdditionalInfo.id == info_id))
    info = result.scalar_one_or_none()
    if info is None:
        raise HTTPException(status_code=404, detail="AdditionalInfo not found")
    return info

@router.get("/", response_model=list[AdditionalInfoRead])
async def get_all_additional_infos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AdditionalInfo))
    infos = result.scalars().all()
    return infos
