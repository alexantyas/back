from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import AsyncSessionLocal
from app.models.team import Team, TeamMember
from app.models.user import User
from app.schemas.team import TeamRead, TeamMemberCreate, TeamMemberRead
from app.routers.auth import get_current_user

router = APIRouter(prefix="/teams", tags=["Teams"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# --- Получить команду текущего тренера ---
@router.get("/my-team", response_model=List[TeamMemberRead])
async def my_team(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Team).where(Team.coach_id == current_user.id))
    team = result.scalar_one_or_none()
    if not team:
        return []
    members_q = await db.execute(select(TeamMember).where(TeamMember.team_id == team.id))
    return members_q.scalars().all()


# --- Получить одну команду (чтобы узнать coach_id) ---
@router.get("/{team_id}", response_model=TeamRead)
async def get_team(team_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


# --- Добавить участника в команду ---
@router.post("/members/", response_model=TeamMemberRead)
async def add_team_member(
    member: TeamMemberCreate,
    db: AsyncSession = Depends(get_db)
):
    new_member = TeamMember(**member.dict())
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    return new_member


# --- Получить участников (опционально по team_id) ---
@router.get("/members/", response_model=List[TeamMemberRead])
async def get_team_members(
    team_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(TeamMember)
    if team_id is not None:
        query = query.where(TeamMember.team_id == team_id)
    result = await db.execute(query)
    return result.scalars().all()


# --- Удалить участника команды ---
@router.delete(
    "/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_team_member(
    member_id: int,
    db: AsyncSession = Depends(get_db)
):
    member = await db.get(TeamMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(member)
    await db.commit()
