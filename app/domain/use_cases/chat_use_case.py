from typing import List, Optional
from uuid import UUID

from app.domain.entities.chat import ChatMessage, ChatRoom
from app.domain.interfaces.repositories.chat_repository import ChatRepository

class ChatUseCase:
    """Handles chat-related business logic."""
    
    def __init__(self, chat_repository: ChatRepository):
        self.chat_repository = chat_repository

    async def send_message(
        self, 
        content: str, 
        sender: str, 
        room_id: str
    ) -> ChatMessage:
        """
        Send a message to a chat room.
        
        Args:
            content: The message content
            sender: ID of the user sending the message
            room_id: ID of the room to send the message to
            
        Returns:
            The created ChatMessage
        """
        message = ChatMessage(
            content=content,
            sender=sender,
            room_id=room_id
        )
        await self.chat_repository.save_message(message)
        return message

    async def get_room_messages(
        self, 
        room_id: str, 
        limit: int = 100
    ) -> List[ChatMessage]:
        """
        Retrieve messages from a chat room.
        
        Args:
            room_id: ID of the room to get messages from
            limit: Maximum number of messages to return
            
        Returns:
            List of ChatMessage objects
        """
        return await self.chat_repository.get_messages(room_id, limit)

    async def create_room(self, name: str) -> ChatRoom:
        """
        Create a new chat room.
        
        Args:
            name: Name of the new room
            
        Returns:
            The created ChatRoom
        """
        return await self.chat_repository.create_room(name)

    async def join_room(self, room_id: str, user_id: str) -> ChatRoom:
        """
        Add a user to a chat room.
        
        Args:
            room_id: ID of the room to join
            user_id: ID of the user joining
            
        Returns:
            The updated ChatRoom
        """
        await self.chat_repository.add_participant(room_id, user_id)
        return await self.chat_repository.get_room(room_id)

    async def leave_room(self, room_id: str, user_id: str) -> ChatRoom:
        """
        Remove a user from a chat room.
        
        Args:
            room_id: ID of the room to leave
            user_id: ID of the user leaving
            
        Returns:
            The updated ChatRoom
        """
        await self.chat_repository.remove_participant(room_id, user_id)
        return await self.chat_repository.get_room(room_id)

    async def list_rooms(self) -> List[ChatRoom]:
        """
        List all available chat rooms.
        
        Returns:
            List of ChatRoom objects
        """
        return await self.chat_repository.list_rooms()

    async def get_room(self, room_id: str) -> Optional[ChatRoom]:
        """
        Get a chat room by ID.
        
        Args:
            room_id: ID of the room to get
            
        Returns:
            The ChatRoom if found, None otherwise
        """
        return await self.chat_repository.get_room(room_id)
