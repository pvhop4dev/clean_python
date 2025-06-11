from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from typing import List, Optional, Callable, Dict, Any
import json
import logging
from uuid import uuid4

from app.domain.entities.chat import ChatMessage, ChatRoom
from app.domain.use_cases.chat_use_case import ChatUseCase
from app.domain.interfaces.repositories.chat_repository import ChatRepository
from app.infrastructure.repositories.chat_repository import InMemoryChatRepository
from app.infrastructure.websocket.connection_manager import manager as connection_manager
from app.presentation.api.v1.dependencies.auth import get_current_user

# Dependency for getting the chat repository
async def get_chat_repository() -> ChatRepository:
    return InMemoryChatRepository()

# Dependency for getting the chat use case
async def get_chat_use_case(
    repository: ChatRepository = Depends(get_chat_repository)
) -> ChatUseCase:
    return ChatUseCase(repository)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: str
):
    """
    WebSocket endpoint for real-time chat.
    
    Args:
        websocket: The WebSocket connection
        room_id: ID of the chat room
        token: JWT token for authentication
    """
    try:
        # Authenticate user
        user = await get_current_user(token)
        user_id = str(user.id)
        
        # Get the chat use case
        # chat_use_case = await get_chat_use_case()
        
        # Connect to the room
        await connection_manager.connect(websocket, room_id, user_id)
        
        try:
            # Join the room
            await chat_use_case.join_room(room_id, user_id)
            
            # Send room info and recent messages
            room = await chat_use_case.get_room(room_id)
            messages = await chat_use_case.get_room_messages(room_id)
            
            await websocket.send_text(json.dumps({
                "type": "room_info",
                "room": room.dict() if room else None,
                "participants": connection_manager.get_room_participants(room_id),
                "messages": [msg.dict() for msg in messages]
            }))
            
            # Handle incoming messages
            while True:
                data = await websocket.receive_text()
                try:
                    message_data = json.loads(data)
                    
                    if message_data.get("type") == "message":
                        # Save and broadcast the message
                        message = await chat_use_case.send_message(
                            content=message_data["content"],
                            sender=user_id,
                            room_id=room_id
                        )
                        
                        # Broadcast to all in the room
                        await connection_manager.broadcast(
                            {
                                "type": "message",
                                "message": message.dict(),
                                "sender_id": user_id
                            },
                            room_id=room_id
                        )
                    
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {data}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        
        except WebSocketDisconnect:
            logger.info(f"Client {user_id} disconnected from room {room_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            # Clean up on disconnect
            connection_manager.disconnect(user_id, room_id)
            chat_use_case = await get_chat_use_case()
            await chat_use_case.leave_room(room_id, user_id)
            
            # Notify room about user leaving
            await connection_manager.broadcast(
                {
                    "type": "user_left",
                    "user_id": user_id,
                    "room_id": room_id,
                    "participants": connection_manager.get_room_participants(room_id)
                },
                room_id=room_id
            )
    
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

@router.get("/rooms", response_model=List[dict])
async def list_rooms(
    chat_use_case: ChatUseCase = Depends(get_chat_use_case)
):
    """List all available chat rooms."""
    return await chat_use_case.list_rooms()

@router.post("/rooms", response_model=ChatRoom)
async def create_room(
    name: str,
    chat_use_case: ChatUseCase = Depends(get_chat_use_case)
):
    """Create a new chat room."""
    return await chat_use_case.create_room(name)

@router.get("/rooms/{room_id}/messages", response_model=List[dict])
async def get_messages(
    room_id: str, 
    limit: int = 100,
    chat_use_case: ChatUseCase = Depends(get_chat_use_case)
):
    """Get messages from a specific room."""
    messages = await chat_use_case.get_room_messages(room_id, limit)
    return [msg.dict() for msg in messages]
