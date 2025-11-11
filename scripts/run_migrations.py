# scripts/run_migrations.py

"""
Run all SQL migrations against Supabase database.

Usage:
    python scripts/run_migrations.py
"""

import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
MIGRATIONS_DIR = PROJECT_ROOT / "backend" / "database" / "migrations"


def get_db_connection():
    """Get database connection."""
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        print("ERROR: SUPABASE_DB_URL not set in environment")
        sys.exit(1)
    return psycopg2.connect(db_url)


def run_migrations():
    """Run all migration files in order."""
    print("🔄 Running database migrations...\n")

    # Get all migration files
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    if not migration_files:
        print("No migration files found")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for migration_file in migration_files:
            print(f"  Running: {migration_file.name}")

            with open(migration_file, "r") as f:
                sql = f.read()

            cursor.execute(sql)
            conn.commit()

            print(f"    ✅ {migration_file.name} completed")

        print(f"\n✅ All {len(migration_files)} migrations completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_migrations()
