import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra='ignore'
    )
    
    # Application
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Database
    DATABASE_URL: str
    DATABASE_SYNC_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 3600
    DB_CONNECT_TIMEOUT: int = 30
    
    # Redis
    REDIS_URL: str
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_TOPIC: str = "fastapi_events"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        # You can add logic here to construct the URL from parts if needed
        return v
    
    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT.lower() == "testing"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
