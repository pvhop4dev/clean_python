from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    sender: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    room_id: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

class ChatRoom(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    participants: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
