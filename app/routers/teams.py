from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.models.team import Team, TeamMember
from app.models.user import User
from app.schemas.team import TeamCreate, TeamRead, TeamMemberCreate, TeamMemberRead
from app.routers.auth import get_current_user
router = APIRouter(prefix="/teams", tags=["Teams"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/members/", response_model=TeamMemberRead)
async def add_team_member(member: TeamMemberCreate, db: AsyncSession = Depends(get_db)):
    new_member = TeamMember(**member.dict())
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    return new_member

@router.get("/members/", response_model=List[TeamMemberRead])
async def get_team_members(
    team_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(TeamMember)
    if team_id:
        query = query.where(TeamMember.team_id == team_id)
    result = await db.execute(query)
    return result.scalars().all()
@router.get("/my-team", response_model=list[TeamMemberRead])
async def my_team(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Находим команду, где тренер — это текущий пользователь
    team = await db.execute(select(Team).where(Team.coach_id == current_user.id))
    team = team.scalar_one_or_none()
    if not team:
        return []

    # Находим участников только этой команды
    members = await db.execute(select(TeamMember).where(TeamMember.team_id == team.id))
    members = members.scalars().all()
    return members
@router.delete("/members/{team_member_id}")
async def delete_team_member(team_member_id: int, db: AsyncSession = Depends(get_db)):
    member = await db.get(TeamMember, team_member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(member)
    await db.commit()
    return {"ok": True}