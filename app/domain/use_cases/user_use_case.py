from typing import Optional, List
from app.domain.entities.user import UserInDB, UserCreate, UserUpdate
from app.domain.interfaces.repositories.user_repository import IUserRepository
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    async def get_user(self, user_id: int) -> Optional[UserInDB]:
        return await self.user_repository.get_by_id(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        return await self.user_repository.get_by_email(email)
    
    async def create_user(self, user: UserCreate) -> UserInDB:
        # Check if user with email already exists
        existing_user = await self.user_repository.get_by_email(user.email)
        if existing_user:
            raise ValueError("User with this email already exists")
            
        # Create new user
        return await self.user_repository.create(user)
    
    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserInDB]:
        # Check if user exists
        existing_user = await self.user_repository.get_by_id(user_id)
        if not existing_user:
            raise ValueError("User not found")
            
        # Check if email is being updated to an existing email
        if user_update.email and user_update.email != existing_user.email:
            email_exists = await self.user_repository.get_by_email(user_update.email)
            if email_exists:
                raise ValueError("Email already in use")
                
        return await self.user_repository.update(user_id, user_update)
    
    async def delete_user(self, user_id: int) -> bool:
        # Check if user exists
        existing_user = await self.user_repository.get_by_id(user_id)
        if not existing_user:
            raise ValueError("User not found")
            
        return await self.user_repository.delete(user_id)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user
