from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.schemas.user import Token, TokenData, UserLogin
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    print("▶ Попытка входа:", form_data.username)

    try:
        result = await db.execute(select(User).where(User.login == form_data.username))
        user = result.scalar_one_or_none()
        print("▶ Пользователь найден:", user)

        if not user or not user.password:
            print("⛔ Пользователь не найден или пустой пароль")
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        if user.password != form_data.password:
            print("⛔ Пароль не совпадает")
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        access_token = create_access_token(data={"sub": user.login})
        print("✅ Токен успешно создан:", access_token)

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        print("💥 ВНУТРЕННЯЯ ОШИБКА:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    result = await db.execute(select(User).where(User.login == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user
