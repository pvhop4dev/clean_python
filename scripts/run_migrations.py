import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from alembic.config import Config
from alembic import command
from app.infrastructure.config import get_settings

def run_migrations():
    print("Running database migrations...")
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    
    # Set up the Alembic configuration
    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', str(script_dir.parent / 'alembic'))
    
    # Get the database URL from settings
    settings = get_settings()
    alembic_cfg.set_main_option('sqlalchemy.url', settings.DATABASE_SYNC_URL)
    
    # Run the migrations
    command.upgrade(alembic_cfg, "head")
    print("Database migrations completed successfully!")

if __name__ == "__main__":
    run_migrations()
