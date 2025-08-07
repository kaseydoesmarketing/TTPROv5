import subprocess
import os

# Set environment variable for database
os.environ['DATABASE_URL'] = "postgresql://ttprov4_db_user:37raL3tdrW0Kl2N2UpePuq9LgsSsjJcP@dpg-d29tuj7diees738ebv8g-a.oregon-postgres.render.com/ttprov4_db"

print("Running database migrations...")

# Run alembic upgrade
result = subprocess.run(
    ["alembic", "upgrade", "head"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✅ Migrations completed successfully!")
    print(result.stdout)
else:
    print("❌ Migration failed!")
    print(result.stderr)