# routers/location.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal

from app.models.user import City, Country
from app.schemas.location import CityRead, CountryRead
from typing import List

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/cities/", response_model=List[CityRead])
async def get_cities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(City))
    return result.scalars().all()

@router.get("/countries/", response_model=List[CountryRead])
async def get_countries(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Country))
    return result.scalars().all()
