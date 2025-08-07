"""
Comprehensive health check for Railway PostgreSQL
Diagnoses connection issues and provides detailed error information
"""

import os
import logging
from sqlalchemy import create_engine, text
import psycopg2
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def diagnose_postgresql_connection():
    """Diagnose PostgreSQL connection issues"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        return {"error": "DATABASE_URL environment variable not set"}
    
    # Parse the URL
    parsed = urlparse(database_url)
    
    connection_info = {
        "scheme": parsed.scheme,
        "host": parsed.hostname,
        "port": parsed.port,
        "database": parsed.path.lstrip('/'),
        "username": parsed.username,
        "has_password": bool(parsed.password)
    }
    
    results = {
        "connection_info": connection_info,
        "tests": {}
    }
    
    # Test 1: Direct psycopg2 connection
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        
        results["tests"]["psycopg2_direct"] = {
            "status": "success",
            "postgres_version": version[0] if version else "unknown"
        }
    except Exception as e:
        results["tests"]["psycopg2_direct"] = {
            "status": "failed",
            "error": str(e)
        }
    
    # Test 2: SQLAlchemy engine
    try:
        # Convert to psycopg2 format if needed
        if database_url.startswith('postgresql://'):
            sqlalchemy_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        else:
            sqlalchemy_url = database_url
            
        engine = create_engine(sqlalchemy_url, connect_args={"connect_timeout": 10})
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database(), current_user;"))
            row = result.fetchone()
            
        results["tests"]["sqlalchemy"] = {
            "status": "success",
            "current_database": row[0] if row else "unknown",
            "current_user": row[1] if row else "unknown"
        }
    except Exception as e:
        results["tests"]["sqlalchemy"] = {
            "status": "failed", 
            "error": str(e)
        }
    
    # Test 3: Check if database exists and is accessible
    try:
        engine = create_engine(sqlalchemy_url)
        with engine.connect() as conn:
            # Check for our tables
            tables_result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in tables_result.fetchall()]
            
        results["tests"]["schema_check"] = {
            "status": "success",
            "tables_found": tables,
            "has_users_table": "users" in tables,
            "has_ab_tests_table": "ab_tests" in tables
        }
    except Exception as e:
        results["tests"]["schema_check"] = {
            "status": "failed",
            "error": str(e)
        }
    
    return results

if __name__ == "__main__":
    import json
    results = diagnose_postgresql_connection()
    print(json.dumps(results, indent=2))