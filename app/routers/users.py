from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.models.team import Team
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.routers.auth import get_current_user  # Только get_current_user, без get_password_hash!

router = APIRouter(prefix="/users", tags=["Users"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Создание пользователя (регистрация)
@router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Создаём пользователя
    new_user = User(**user.dict())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # 2. Если роль — тренер, создаём команду
    if new_user.role_id == 2:  # 2 — coach
        new_team = Team(name=f"Команда {new_user.last_name}", coach_id=new_user.id)
        db.add(new_team)
        await db.commit()
        await db.refresh(new_team)

    return new_user
# Получение текущего пользователя по токену (JWT)
@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
# Получение пользователя по id (требует токен)
@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


