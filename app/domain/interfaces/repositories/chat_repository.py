from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.chat import ChatMessage, ChatRoom

class ChatRepository(ABC):
    """Abstract base class for chat repository operations."""
    
    @abstractmethod
    async def save_message(self, message: ChatMessage) -> None:
        """Save a chat message to the repository."""
        pass
    
    @abstractmethod
    async def get_messages(self, room_id: str, limit: int = 100) -> List[ChatMessage]:
        """Retrieve messages for a specific room."""
        pass
    
    @abstractmethod
    async def get_room(self, room_id: str) -> Optional[ChatRoom]:
        """Get a chat room by ID."""
        pass
    
    @abstractmethod
    async def create_room(self, room_name: str) -> ChatRoom:
        """Create a new chat room."""
        pass
    
    @abstractmethod
    async def add_participant(self, room_id: str, user_id: str) -> None:
        """Add a participant to a chat room."""
        pass
    
    @abstractmethod
    async def remove_participant(self, room_id: str, user_id: str) -> None:
        """Remove a participant from a chat room."""
        pass
    
    @abstractmethod
    async def list_rooms(self) -> List[ChatRoom]:
        """List all available chat rooms."""
        pass
