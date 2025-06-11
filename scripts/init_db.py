import asyncio
import sys
import time
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.infrastructure.database import async_engine
from app.infrastructure.config import get_settings

async def init_models():
    max_retries = 5
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            print(f"Attempting to connect to database (Attempt {attempt + 1}/{max_retries})...")
            
            # Test the connection first
            async with async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            
            # If we get here, connection was successful
            print("Connection to database successful!")
            return True
            
        except OperationalError as e:
            print(f"Database connection failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Giving up.")
                return False

if __name__ == "__main__":
    if not asyncio.run(init_models()):
        sys.exit(1)
