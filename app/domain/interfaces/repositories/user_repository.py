from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.user import UserInDB, UserCreate, UserUpdate

class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        pass
    
    @abstractmethod
    async def create(self, user: UserCreate) -> UserInDB:
        pass
    
    @abstractmethod
    async def update(self, user_id: int, user_update: UserUpdate) -> Optional[UserInDB]:
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        pass
