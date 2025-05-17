from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import AsyncSessionLocal
from app.models.application import (
    Application,
    RequestType,
    ApplicationTeamParticipant,
    ApplicationIndividualParticipant,
)
from app.schemas.application import (
    ApplicationCreate, ApplicationRead,
    RequestTypeCreate, RequestTypeRead,
    ApplicationTeamParticipantCreate, ApplicationTeamParticipantRead,
    ApplicationIndividualParticipantCreate, ApplicationIndividualParticipantRead,
)

router = APIRouter(prefix="/applications", tags=["Applications"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- Создание заявки с участниками ---
@router.post("/", response_model=ApplicationRead)
async def create_application(application: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    new_application = Application(
        competition_id=application.competition_id,
        request_type_id=application.request_type_id,
        team_id=application.team_id,
        request_date=application.request_date,
    )
    db.add(new_application)
    await db.flush()  # получаем ID заявки

    # Добавление командных участников
    if application.team_participants:
        for p in application.team_participants:
            data = p.dict()
            data.pop("application_id", None)
            db.add(ApplicationTeamParticipant(
                application_id=new_application.id,
                **data
            ))

    # Добавление индивидуальных участников
    if application.individual_participants:
        for p in application.individual_participants:
            data = p.dict()
            data.pop("application_id", None)
            db.add(ApplicationIndividualParticipant(
                application_id=new_application.id,
                **data
            ))

    await db.commit()
    await db.refresh(new_application)
    return new_application

# --- Получение всех заявок ---
@router.get("/", response_model=List[ApplicationRead])
async def get_all_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application))
    return result.scalars().all()

# --- Добавление индивидуального участника ---
@router.post("/participants/individual/", response_model=ApplicationIndividualParticipantRead)
async def add_individual_participant(
    participant: ApplicationIndividualParticipantCreate,
    db: AsyncSession = Depends(get_db)
):
    new_participant = ApplicationIndividualParticipant(**participant.dict())
    db.add(new_participant)
    await db.commit()
    await db.refresh(new_participant)
    return new_participant

# --- Получение всех индивидуальных участников ---
@router.get("/participants/individual/", response_model=List[ApplicationIndividualParticipantRead])
async def get_all_individual_participants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApplicationIndividualParticipant))
    return result.scalars().all()

# --- Добавление командного участника ---
@router.post("/participants/team/", response_model=ApplicationTeamParticipantRead)
async def add_team_participant(
    participant: ApplicationTeamParticipantCreate,
    db: AsyncSession = Depends(get_db)
):
    new_participant = ApplicationTeamParticipant(**participant.dict())
    db.add(new_participant)
    await db.commit()
    await db.refresh(new_participant)
    return new_participant

# --- Получение всех командных участников ---
@router.get("/participants/team/", response_model=List[ApplicationTeamParticipantRead])
async def get_all_team_participants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApplicationTeamParticipant))
    return result.scalars().all()

# --- Работа с типами заявок ---
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
