import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory of Project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file
ENV_PATH = BASE_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

class Config:
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
    
    # Database Type: 'sqlite' or 'oracle'
    DB_TYPE = os.getenv('DB_TYPE', 'sqlite').lower()
    
    # SQLite Configuration
    SQLITE_DB_PATH = os.getenv(
        'SQLITE_DB_PATH', 
        str(BASE_DIR / 'database' / 'event_management.db')
    )
    
    # Oracle SQL Configuration
    ORACLE_USER = os.getenv('ORACLE_USER', 'system')
    ORACLE_PASSWORD = os.getenv('ORACLE_PASSWORD', '')
    ORACLE_HOST = os.getenv('ORACLE_HOST', 'localhost')
    ORACLE_PORT = int(os.getenv('ORACLE_PORT', 1521))
    ORACLE_SERVICE_NAME = os.getenv('ORACLE_SERVICE_NAME', 'XEPDB1')
    ORACLE_SID = os.getenv('ORACLE_SID', '')
    
    # Schema & Seed SQL File Paths
    SCHEMA_SQLITE_PATH = BASE_DIR / 'database' / 'schema' / 'schema_sqlite.sql'
    SCHEMA_ORACLE_PATH = BASE_DIR / 'database' / 'schema' / 'schema_oracle.sql'
    SEED_SQLITE_PATH = BASE_DIR / 'database' / 'seed' / 'seed_sqlite.sql'
    SEED_ORACLE_PATH = BASE_DIR / 'database' / 'seed' / 'seed_oracle.sql'
