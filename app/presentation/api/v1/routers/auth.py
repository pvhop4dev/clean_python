from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from app.domain.entities.user import Token, UserCreate, UserInDB
from app.presentation.api.v1.dependencies import get_user_use_case
from app.domain.use_cases.user_use_case import UserUseCase
from app.infrastructure.config import get_settings
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_use_case: UserUseCase = Depends(get_user_use_case)
):
    user = await user_use_case.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    user_use_case: UserUseCase = Depends(get_user_use_case)
):
    try:
        user = await user_use_case.create_user(user_create)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
