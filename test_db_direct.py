#!/usr/bin/env python3
import psycopg2
import os

# Test direct database connection
DATABASE_URL = "postgresql://ttprov4_db_user:37raL3tdrW0Kl2N2UpePuq9LgsSsjJcP@dpg-d29tuj7diees738ebv8g-a.oregon-postgres.render.com/ttprov4_db"

print("Testing direct database connection...")
print(f"URL: {DATABASE_URL}")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    print(f"✅ Connection successful: {result}")
    
    # Test if tables exist
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    print(f"Tables in database: {[t[0] for t in tables]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")