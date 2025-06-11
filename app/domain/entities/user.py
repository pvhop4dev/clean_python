from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any
from datetime import datetime, timezone, timedelta

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=30))
    user_id: Optional[int] = None
    username: Optional[str] = None

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    exp: Optional[datetime] = None

class UserBase(BaseModel):
    """Base user model containing common attributes."""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    """Database model for user with sensitive information."""
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
