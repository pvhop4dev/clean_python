import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from app.infrastructure.config import get_settings
import asyncio
import time

settings = get_settings()

# Add connection pooling and timeout settings
DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '5'))
DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '10'))
DB_POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', '3600'))
DB_CONNECT_TIMEOUT = int(os.getenv('DB_CONNECT_TIMEOUT', '30'))

# Async engine with connection pooling
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_recycle=DB_POOL_RECYCLE,
    pool_pre_ping=True,
    connect_args={"connect_timeout": DB_CONNECT_TIMEOUT}
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Sync engine for migrations
sync_engine = create_engine(
    settings.DATABASE_SYNC_URL,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_recycle=DB_POOL_RECYCLE,
    pool_pre_ping=True,
    connect_args={"connect_timeout": DB_CONNECT_TIMEOUT}
)

SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async DB session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

async def init_database():
    """Initialize database tables"""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("Database tables created successfully!")
            return True
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Database not ready, retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(retry_delay)
            else:
                print("Failed to initialize database after maximum retries")
                raise e
