import os
import psycopg2
from psycopg2 import OperationalError

# Test database connection
# Try external hostname
DATABASE_URL = "postgresql://ttprov4_db_user:37raL3tdrW0Kl2N2UpePuq9LgsSsjJcP@dpg-d29tuj7diees738ebv8g-a.oregon-postgres.render.com/ttprov4_db"

try:
    # Parse the DATABASE_URL
    # Format: postgresql://user:password@host/database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Test query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ Database connection successful!")
    print(f"PostgreSQL version: {version[0]}")
    
    # Check if tables exist
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    print(f"\nTables in database: {[t[0] for t in tables]}")
    
    cursor.close()
    conn.close()
    
except OperationalError as e:
    print(f"❌ Database connection failed: {e}")
except Exception as e:
    print(f"❌ Error: {e}")