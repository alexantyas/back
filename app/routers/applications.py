# app/routers/applications.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
    ApplicationCreate,
    ApplicationRead,
    RequestTypeCreate,
    RequestTypeRead,
    ApplicationTeamParticipantCreate,
    ApplicationTeamParticipantRead,
    ApplicationIndividualParticipantCreate,
    ApplicationIndividualParticipantRead,
    ApplicationUpdate,
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Создаёт новую заявку (pending), добавляет участников и возвращает её
    с полными связями (user, individual_participants, team_participants).
    """
    new_application = Application(
        competition_id=application.competition_id,
        request_type_id=application.request_type_id,
        team_id=application.team_id,
        request_date=application.request_date,
        user_id=current_user.id,
        status="pending",
    )
    db.add(new_application)
    await db.flush()

    if application.team_participants:
        for p in application.team_participants:
            data = p.dict(exclude={"application_id"})
            db.add(
                ApplicationTeamParticipant(
                    application_id=new_application.id, **data
                )
            )

    if application.individual_participants:
        for p in application.individual_participants:
            data = p.dict(exclude={"application_id"})
            db.add(
                ApplicationIndividualParticipant(
                    application_id=new_application.id, **data
                )
            )

    await db.commit()

    # Eager-загружаем связи, чтобы Pydantic не пытался делать асинхронные lazy-operation
    q = (
        select(Application)
        .where(Application.id == new_application.id)
        .options(
            selectinload(Application.user),
            selectinload(Application.individual_participants),
            selectinload(Application.team_participants),
        )
    )
    result = await db.execute(q)
    created = result.scalars().first()
    return created


@router.get("/", response_model=List[ApplicationRead])
async def get_all_applications(
    competition_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Возвращает список заявок. Если передан competition_id, то только для него.
    Включает user, individual_participants, team_participants и команду.
    """
    q = (
        select(Application)
        .options(
            selectinload(Application.individual_participants),
            selectinload(Application.team_participants),
            selectinload(Application.team),
            selectinload(Application.user),
        )
    )
    if competition_id is not None:
        q = q.where(Application.competition_id == competition_id)

    result = await db.execute(q)
    return result.scalars().all()


# --- CRUD для участников заявки ---

@router.post(
    "/participants/individual/",
    response_model=ApplicationIndividualParticipantRead,
)
async def add_individual_participant(
    participant: ApplicationIndividualParticipantCreate,
    db: AsyncSession = Depends(get_db),
):
    new = ApplicationIndividualParticipant(**participant.dict())
    db.add(new)
    await db.commit()
    await db.refresh(new)
    return new


@router.get(
    "/participants/individual/",
    response_model=List[ApplicationIndividualParticipantRead],
)
async def get_all_individual_participants(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ApplicationIndividualParticipant))
    return result.scalars().all()


@router.post(
    "/participants/team/",
    response_model=ApplicationTeamParticipantRead,
)
async def add_team_participant(
    participant: ApplicationTeamParticipantCreate,
    db: AsyncSession = Depends(get_db),
):
    new = ApplicationTeamParticipant(**participant.dict())
    db.add(new)
    await db.commit()
    await db.refresh(new)
    return new


@router.get(
    "/participants/team/",
    response_model=List[ApplicationTeamParticipantRead],
)
async def get_all_team_participants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApplicationTeamParticipant))
    return result.scalars().all()


# --- Типы заявок ---

@router.post(
    "/request-types/",
    response_model=RequestTypeRead,
)
async def create_request_type(
    request_type: RequestTypeCreate,
    db: AsyncSession = Depends(get_db),
):
    new = RequestType(**request_type.dict())
    db.add(new)
    await db.commit()
    await db.refresh(new)
    return new


@router.get(
    "/request-types/",
    response_model=List[RequestTypeRead],
)
async def get_request_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RequestType))
    return result.scalars().all()


@router.patch(
    "/{app_id}",
    response_model=ApplicationRead,
    summary="Частичное обновление заявки (обычно — смена статуса)",
)
async def update_application(
    app_id: int,
    app_upd: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Меняет поля заявки (например, статус), коммитит и
    возвращает её заново с полными связями.
    """
    db_app = await db.get(Application, app_id)
    if not db_app:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    for field, value in app_upd.dict(exclude_unset=True).items():
        setattr(db_app, field, value)

    db.add(db_app)
    await db.commit()

    # Перезапрос с eager-загрузкой связей
    q = (
        select(Application)
        .where(Application.id == app_id)
        .options(
            selectinload(Application.user),
            selectinload(Application.individual_participants),
            selectinload(Application.team_participants),
        )
    )
    result = await db.execute(q)
    updated_app = result.scalars().first()
    if not updated_app:
        raise HTTPException(status_code=404, detail="Заявка неожиданно пропала")

    return updated_app
