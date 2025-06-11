from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.infrastructure.config import get_settings
from app.presentation.api.v1.routers import auth, users
from app.presentation.api.v1.endpoints import chat

settings = get_settings()

def create_application() -> FastAPI:
    application = FastAPI(
        title="FastAPI Clean Architecture",
        description="FastAPI application with Clean Architecture",
        version="0.1.0",
    )

    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    application.include_router(auth.router, prefix="/api/v1", tags=["auth"])
    application.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    application.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
    
    # Mount static files for WebSocket demo
    os.makedirs("static", exist_ok=True)
    application.mount("/static", StaticFiles(directory="static"), name="static")

    return application

app = create_application()

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Clean Architecture"}
