#!/usr/bin/env python3
import os

# What the DATABASE_URL should be
expected_external_url = "postgresql://ttprov4_db_user:37raL3tdrW0Kl2N2UpePuq9LgsSsjJcP@dpg-d29tuj7diees738ebv8g-a.oregon-postgres.render.com/ttprov4_db"

# What it probably is now (internal)
internal_url = "postgresql://ttprov4_db_user:37raL3tdrW0Kl2N2UpePuq9LgsSsjJcP@dpg-d29tuj7diees738ebv8g-a/ttprov4_db"

print("DATABASE_URL Configuration Check")
print("=" * 50)
print("\n❌ INTERNAL URL (won't work in Docker):")
print(f"   {internal_url}")
print("\n✅ EXTERNAL URL (required for Docker):")
print(f"   {expected_external_url}")
print("\nThe difference is adding '.oregon-postgres.render.com' to the hostname")
print("\nTo fix:")
print("1. Go to Render Dashboard → Backend Service → Environment")
print("2. Update DATABASE_URL to the external URL above")
print("3. Save and the service will redeploy")