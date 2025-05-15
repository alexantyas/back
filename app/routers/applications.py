from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.models.application import Application, ApplicationParticipant, RequestType
from app.schemas.application import (
    ApplicationCreate, ApplicationRead,
    ApplicationParticipantCreate, ApplicationParticipantRead,
    RequestTypeCreate, RequestTypeRead,
)

router = APIRouter(prefix="/applications", tags=["Applications"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=ApplicationRead)
async def create_application(application: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    new_application = Application(**application.dict())
    db.add(new_application)
    await db.commit()
    await db.refresh(new_application)
    return new_application

@router.get("/", response_model=List[ApplicationRead])
async def get_all_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application))
    return result.scalars().all()

@router.post("/participants/", response_model=ApplicationParticipantRead)
async def add_participant(participant: ApplicationParticipantCreate, db: AsyncSession = Depends(get_db)):
    new_participant = ApplicationParticipant(**participant.dict())
    db.add(new_participant)
    await db.commit()
    await db.refresh(new_participant)
    return new_participant

@router.get("/participants/", response_model=List[ApplicationParticipantRead])
async def get_all_participants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApplicationParticipant))
    return result.scalars().all()

@router.post("/request-types/", response_model=RequestTypeRead)
async def create_request_type(request_type: RequestTypeCreate, db: AsyncSession = Depends(get_db)):
    new_type = RequestType(**request_type.dict())
    db.add(new_type)
    await db.commit()
    await db.refresh(new_type)
    return new_type

@router.get("/request-types/", response_model=List[RequestTypeRead])
async def get_request_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RequestType))
    return result.scalars().all()
