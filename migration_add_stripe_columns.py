#!/usr/bin/env python3
"""
PostgreSQL migration to add missing Stripe columns to users table
Fixes the missing users.stripe_customer_id column causing authentication failures
"""

import os
import psycopg2
from urllib.parse import urlparse

def run_migration():
    print("🔧 PostgreSQL Migration - Adding Stripe Columns")
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False

    print(f"📁 Database URL found: {database_url[:50]}...")

    url = urlparse(database_url)

    conn = None
    try:
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            database=url.path[1:],
            user=url.username,
            password=url.password
        )
        cursor = conn.cursor()

        print("✅ Connected to PostgreSQL")

        migrations = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status VARCHAR DEFAULT 'free';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_plan VARCHAR DEFAULT 'free';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_period_end TIMESTAMP;",
        ]

        for migration in migrations:
            try:
                cursor.execute(migration)
                print(f"✅ Executed: {migration}")
            except Exception as e:
                print(f"⚠️ Migration may already exist: {e}")

        conn.commit()
        print("✅ All migrations completed successfully")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()
            print("🔌 Database connection closed")

if __name__ == "__main__":
    print("=" * 50)
    print("PostgreSQL Migration - Add Stripe Columns")
    print("=" * 50)
    success = run_migration()
    print("=" * 50)
    if success:
        print("🎉 Migration completed successfully!")
        print("✅ Missing Stripe columns have been added to users table")
    else:
        print("❌ Migration failed!")
    print("=" * 50)
