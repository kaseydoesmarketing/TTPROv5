"""
Application startup checks and validations
"""

from .database import engine
from .database_utils import validate_database_schema, fix_sqlite_schema_issues
import logging

logger = logging.getLogger(__name__)

def run_startup_checks():
    """
    Run startup checks to ensure database compatibility
    """
    logger.info("Running startup database checks...")
    
    # Validate SQLite schema compatibility
    issues = validate_database_schema(engine)
    
    if issues:
        logger.warning("SQLite compatibility issues found:")
        for issue in issues:
            logger.warning(f"  - {issue}")
            
        # Attempt to fix issues automatically
        logger.info("Attempting to fix compatibility issues...")
        if fix_sqlite_schema_issues(engine, issues):
            logger.info("✅ All compatibility issues resolved")
        else:
            logger.error("❌ Manual intervention required for database schema")
            logger.error("Please run database migrations or contact support")
    else:
        logger.info("✅ Database schema is SQLite compatible")