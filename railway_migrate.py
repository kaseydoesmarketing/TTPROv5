#!/usr/bin/env python3
"""
Railway-specific database migration script
Handles database initialization and migrations for Railway deployment
"""
import os
import sys
import logging
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_exists(database_url: str) -> bool:
    """Check if database exists and is accessible"""
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def run_migrations():
    """Run Alembic migrations"""
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("❌ DATABASE_URL environment variable not set")
            sys.exit(1)
        
        # Check database connection
        if not check_database_exists(database_url):
            logger.error("❌ Cannot connect to database")
            sys.exit(1)
        
        # Run migrations
        logger.info("🚀 Running database migrations...")
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        # Upgrade to latest revision
        command.upgrade(alembic_cfg, "head")
        
        logger.info("✅ Migrations completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)