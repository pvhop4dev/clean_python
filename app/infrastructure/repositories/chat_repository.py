from typing import Dict, List, Optional
from uuid import uuid4

from app.domain.entities.chat import ChatMessage, ChatRoom
from app.domain.interfaces.repositories.chat_repository import ChatRepository

class InMemoryChatRepository(ChatRepository):
    """In-memory implementation of ChatRepository for development and testing."""
    
    def __init__(self):
        self.messages: Dict[str, List[ChatMessage]] = {}
        self.rooms: Dict[str, ChatRoom] = {}
        # Create a default room
        self._create_default_room()
    
    def _create_default_room(self):
        """Create a default general chat room."""
        default_room = ChatRoom(
            id="general",
            name="General Chat"
        )
        self.rooms[default_room.id] = default_room
        self.messages[default_room.id] = []
    
    async def save_message(self, message: ChatMessage) -> None:
        """Save a message to the repository."""
        if message.room_id not in self.messages:
            self.messages[message.room_id] = []
        self.messages[message.room_id].append(message)
    
    async def get_messages(self, room_id: str, limit: int = 100) -> List[ChatMessage]:
        """Get messages for a room, most recent first."""
        room_messages = self.messages.get(room_id, [])
        # Return most recent messages first
        return sorted(room_messages, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    async def get_room(self, room_id: str) -> Optional[ChatRoom]:
        """Get a room by ID."""
        return self.rooms.get(room_id)
    
    async def create_room(self, name: str) -> ChatRoom:
        """Create a new chat room."""
        room_id = str(uuid4())
        room = ChatRoom(
            id=room_id,
            name=name
        )
        self.rooms[room_id] = room
        self.messages[room_id] = []
        return room
    
    async def add_participant(self, room_id: str, user_id: str) -> None:
        """Add a participant to a room."""
        if room_id not in self.rooms:
            # Create the room if it doesn't exist
            await self.create_room(f"Room {room_id}")
            
        if user_id not in self.rooms[room_id].participants:
            self.rooms[room_id].participants.append(user_id)
    
    async def remove_participant(self, room_id: str, user_id: str) -> None:
        """Remove a participant from a room."""
        if room_id in self.rooms:
            if user_id in self.rooms[room_id].participants:
                self.rooms[room_id].participants.remove(user_id)
    
    async def list_rooms(self) -> List[ChatRoom]:
        """List all available rooms."""
        return list(self.rooms.values())
