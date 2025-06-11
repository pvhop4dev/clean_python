from typing import Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.user import UserInDB, UserCreate, UserUpdate
from app.domain.interfaces.repositories.user_repository import IUserRepository
from app.infrastructure.database.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository(IUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        return UserInDB.model_validate(user) if user else None
    
    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        result = await self.db.execute(select(User).filter(User.email == email))
        user = result.scalars().first()
        return UserInDB.model_validate(user) if user else None
    
    async def create(self, user: UserCreate) -> UserInDB:
        hashed_password = pwd_context.hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password,
            is_active=user.is_active
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return UserInDB.model_validate(db_user)
    
    async def update(self, user_id: int, user_update: UserUpdate) -> Optional[UserInDB]:
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))
        
        stmt = update(User).where(User.id == user_id).values(**update_data).returning(User)
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        updated_user = result.scalars().first()
        return UserInDB.model_validate(updated_user) if updated_user else None
    
    async def delete(self, user_id: int) -> bool:
        stmt = delete(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
