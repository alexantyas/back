from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.models.application import (
    Application,
    RequestType,
    ApplicationTeamParticipant,
    ApplicationIndividualParticipant,
)
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate, ApplicationRead,
    RequestTypeCreate, RequestTypeRead,
    ApplicationTeamParticipantCreate, ApplicationTeamParticipantRead,
    ApplicationIndividualParticipantCreate, ApplicationIndividualParticipantRead,
)
from app.routers.auth import get_current_user
from app.schemas.user import UserRead

router = APIRouter(prefix="/applications", tags=["Applications"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=ApplicationRead)
async def create_application(
    application: ApplicationCreate,
    current_user: User = Depends(get_current_user),  # ← получаем из JWT
    db: AsyncSession = Depends(get_db)
):
    new_application = Application(
        competition_id=application.competition_id,
        request_type_id=application.request_type_id,
        team_id=application.team_id,
        request_date=application.request_date,
        user_id=current_user.id                           # ← сохраняем тренера
    )
    db.add(new_application)
    await db.flush()

    if application.team_participants:
        for p in application.team_participants:
            data = p.dict(exclude={"application_id"})
            db.add(ApplicationTeamParticipant(application_id=new_application.id, **data))

    if application.individual_participants:
        for p in application.individual_participants:
            data = p.dict(exclude={"application_id"})
            db.add(ApplicationIndividualParticipant(application_id=new_application.id, **data))

    await db.commit()
    await db.refresh(new_application)
    return new_application


@router.get("/", response_model=List[ApplicationRead])
async def get_all_applications(
    competition_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Если передан ?competition_id=, то отдаём только
    заявки для этого соревнования.
    """
    q = select(Application).options(
        selectinload(Application.individual_participants),
        selectinload(Application.team_participants),
        selectinload(Application.team),
        selectinload(Application.user),
    )
    if competition_id is not None:
        q = q.where(Application.competition_id == competition_id)

    result = await db.execute(q)
    return result.scalars().all()

# --- CRUD для участников (без изменений) --- #

@router.post("/participants/individual/", response_model=ApplicationIndividualParticipantRead)
async def add_individual_participant(
    participant: ApplicationIndividualParticipantCreate,
    db: AsyncSession = Depends(get_db)
):
    new = ApplicationIndividualParticipant(**participant.dict())
    db.add(new)
    await db.commit()
    await db.refresh(new)
    return new

@router.get("/participants/individual/", response_model=List[ApplicationIndividualParticipantRead])
async def get_all_individual_participants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApplicationIndividualParticipant))
    return result.scalars().all()

@router.post("/participants/team/", response_model=ApplicationTeamParticipantRead)
async def add_team_participant(
    participant: ApplicationTeamParticipantCreate,
    db: AsyncSession = Depends(get_db)
):
    new = ApplicationTeamParticipant(**participant.dict())
    db.add(new)
    await db.commit()
    await db.refresh(new)
    return new

@router.get("/participants/team/", response_model=List[ApplicationTeamParticipantRead])
async def get_all_team_participants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApplicationTeamParticipant))
    return result.scalars().all()


# --- Типы заявок (не изменились) --- #

@router.post("/request-types/", response_model=RequestTypeRead)
async def create_request_type(request_type: RequestTypeCreate, db: AsyncSession = Depends(get_db)):
    new = RequestType(**request_type.dict())
    db.add(new)
    await db.commit()
    await db.refresh(new)
    return new

@router.get("/request-types/", response_model=List[RequestTypeRead])
async def get_request_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RequestType))
    return result.scalars().all()
