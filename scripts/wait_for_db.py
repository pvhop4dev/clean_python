import os
import sys
import time
import pymysql
from pymysql import OperationalError
from app.infrastructure.config import get_settings

def wait_for_db():
    """Wait for the database to be available."""
    settings = get_settings()
    max_retries = 30
    retry_delay = 2  # seconds
    
    # Extract database connection details from the URL
    db_url = settings.DATABASE_SYNC_URL
    if db_url.startswith('mysql+pymysql://'):
        db_url = db_url.replace('mysql+pymysql://', '')
    
    user_pass, host_port_db = db_url.split('@')
    user, password = user_pass.split(':')
    host_port, db = host_port_db.split('/')
    
    if ':' in host_port:
        host, port = host_port.split(':')
    else:
        host = host_port
        port = 3306
    
    print(f"Waiting for database at {host}:{port}...")
    
    for i in range(max_retries):
        try:
            conn = pymysql.connect(
                host=host,
                port=int(port),
                user=user,
                password=password,
                database=db,
                connect_timeout=5
            )
            conn.ping()
            conn.close()
            print("Database is ready!")
            return True
        except OperationalError as e:
            if i < max_retries - 1:
                print(f"Database not ready yet. Retrying in {retry_delay} seconds... (Attempt {i + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect to database after {max_retries} attempts")
                print(f"Error: {e}")
                return False

if __name__ == "__main__":
    if not wait_for_db():
        sys.exit(1)
