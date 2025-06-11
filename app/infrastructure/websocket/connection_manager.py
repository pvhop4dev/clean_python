from typing import Dict, List, Set, Optional
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    """Manages WebSocket connections and broadcasting."""
    
    def __init__(self):
        # room_id -> {user_id -> WebSocket}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # room_id -> set of user_ids
        self.room_participants: Dict[str, Set[str]] = {}
        # user_id -> set of room_ids
        self.user_rooms: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, user_id: str) -> None:
        """Accept a new WebSocket connection and add to room."""
        await websocket.accept()
        
        # Initialize room if it doesn't exist
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
            self.room_participants[room_id] = set()
        
        # Add connection
        self.active_connections[room_id][user_id] = websocket
        self.room_participants[room_id].add(user_id)
        
        # Track user's rooms
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()
        self.user_rooms[user_id].add(room_id)
        
        # Notify room about new user
        await self.broadcast(
            {
                "type": "user_joined",
                "user_id": user_id,
                "room_id": room_id,
                "timestamp": datetime.utcnow().isoformat(),
                "participants": list(self.room_participants[room_id])
            },
            room_id=room_id,
            exclude_user_id=user_id
        )
    
    def disconnect(self, user_id: str, room_id: Optional[str] = None) -> None:
        """Remove a user's connection from one or all rooms."""
        if room_id:
            self._remove_connection(user_id, room_id)
        elif user_id in self.user_rooms:
            # Remove from all rooms
            for room_id in list(self.user_rooms[user_id]):
                self._remove_connection(user_id, room_id)
    
    def _remove_connection(self, user_id: str, room_id: str) -> None:
        """Internal method to remove a user from a specific room."""
        if room_id in self.active_connections and user_id in self.active_connections[room_id]:
            # Remove the connection
            del self.active_connections[room_id][user_id]
            
            # Clean up empty rooms
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                if room_id in self.room_participants:
                    del self.room_participants[room_id]
            elif room_id in self.room_participants and user_id in self.room_participants[room_id]:
                self.room_participants[room_id].remove(user_id)
            
            # Update user's room tracking
            if user_id in self.user_rooms and room_id in self.user_rooms[user_id]:
                self.user_rooms[user_id].remove(room_id)
                if not self.user_rooms[user_id]:
                    del self.user_rooms[user_id]
    
    async def send_personal_message(self, message: dict, user_id: str) -> None:
        """Send a message to a specific user in all their connected rooms."""
        if user_id not in self.user_rooms:
            return
            
        message_str = json.dumps(message)
        tasks = []
        
        for room_id in self.user_rooms[user_id]:
            if room_id in self.active_connections and user_id in self.active_connections[room_id]:
                websocket = self.active_connections[room_id][user_id]
                tasks.append(websocket.send_text(message_str))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast(self, message: dict, room_id: str, exclude_user_id: str = None) -> None:
        """Broadcast a message to all users in a room."""
        if room_id not in self.active_connections:
            return
            
        message_str = json.dumps(message)
        tasks = []
        
        for user_id, connection in self.active_connections[room_id].items():
            if user_id != exclude_user_id:  # Skip excluded user
                tasks.append(connection.send_text(message_str))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_room_participants(self, room_id: str) -> List[str]:
        """Get list of user IDs in a room."""
        return list(self.room_participants.get(room_id, []))
    
    def get_user_rooms(self, user_id: str) -> List[str]:
        """Get list of room IDs a user is in."""
        return list(self.user_rooms.get(user_id, []))

# Singleton instance
manager = ConnectionManager()
