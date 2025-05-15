from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.models.team import Team, TeamMember
from app.schemas.team import TeamCreate, TeamRead, TeamMemberCreate, TeamMemberRead

router = APIRouter(prefix="/teams", tags=["Teams"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=TeamRead)
async def create_team(team: TeamCreate, db: AsyncSession = Depends(get_db)):
    new_team = Team(**team.dict())
    db.add(new_team)
    await db.commit()
    await db.refresh(new_team)
    return new_team

@router.get("/", response_model=List[TeamRead])
async def get_all_teams(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team))
    return result.scalars().all()

@router.post("/members/", response_model=TeamMemberRead)
async def add_team_member(member: TeamMemberCreate, db: AsyncSession = Depends(get_db)):
    new_member = TeamMember(**member.dict())
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    return new_member

@router.get("/members/", response_model=List[TeamMemberRead])
async def get_all_team_members(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TeamMember))
    return result.scalars().all()
