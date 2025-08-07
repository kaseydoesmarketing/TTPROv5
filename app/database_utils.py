"""
Database utility functions for SQLite compatibility
"""

from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine
import logging

logger = logging.getLogger(__name__)

def get_database_compatible_datetime():
    """Return database-compatible datetime expression for current timestamp"""
    # For PostgreSQL: NOW() or CURRENT_TIMESTAMP
    # For SQLite: datetime('now')
    # Use PostgreSQL syntax since production uses PostgreSQL
    return text("NOW()")

def validate_database_schema(engine: Engine) -> list:
    """
    Validate that the current database schema is SQLite compatible
    Returns list of issues found
    """
    issues = []
    
    if engine.dialect.name != 'sqlite':
        return issues  # Only validate SQLite databases
        
    inspector = inspect(engine)
    
    try:
        # Check each table's schema
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            
            for column in columns:
                # Check for problematic default values
                if column.get('default'):
                    default_str = str(column['default'])
                    if 'now()' in default_str.lower() and 'datetime(' not in default_str.lower():
                        issues.append(
                            f"Table '{table_name}', column '{column['name']}' "
                            f"has incompatible default: {default_str}"
                        )
                        
    except Exception as e:
        logger.error(f"Error validating database schema: {e}")
        issues.append(f"Schema validation error: {e}")
    
    return issues

def fix_sqlite_schema_issues(engine: Engine, issues: list) -> bool:
    """
    Attempt to fix SQLite schema issues automatically
    Returns True if all issues were fixed
    """
    if engine.dialect.name != 'sqlite':
        return True  # Nothing to fix for non-SQLite databases
        
    try:
        with engine.connect() as conn:
            # This is a simplified fix - in practice, you'd need more sophisticated logic
            # to handle table recreation with proper foreign key handling
            logger.info("Automatic schema fixes would be implemented here")
            # For now, just log the issues that need manual attention
            for issue in issues:
                logger.warning(f"Manual fix needed: {issue}")
        return False  # Indicate manual intervention needed
    except Exception as e:
        logger.error(f"Error fixing schema issues: {e}")
        return False

def create_migration_for_sqlite_compatibility(engine: Engine) -> str:
    """
    Generate a migration script to fix SQLite compatibility issues
    Returns the migration SQL
    """
    migration_sql = """
-- SQLite Compatibility Migration
-- Generated automatically to fix datetime function issues

-- This migration would contain the specific ALTER statements
-- needed to fix any identified compatibility issues

-- Example:
-- ALTER TABLE table_name ...;

-- Note: Actual implementation would generate specific fixes
-- based on the issues found in validate_database_schema()
"""
    return migration_sql