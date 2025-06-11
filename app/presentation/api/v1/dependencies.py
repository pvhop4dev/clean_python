from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
from app.infrastructure.database import get_db, AsyncSession
from app.infrastructure.config import get_settings
from app.infrastructure.repositories.user_repository import UserRepository
from app.domain.use_cases.user_use_case import UserUseCase

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

# Dependency
def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

# Dependency
def get_user_use_case(user_repo: UserRepository = Depends(get_user_repository)) -> UserUseCase:
    return UserUseCase(user_repo)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_use_case: UserUseCase = Depends(get_user_use_case)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await user_use_case.get_user_by_email(username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: UserUseCase = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
