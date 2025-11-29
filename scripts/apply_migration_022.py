#!/usr/bin/env python3
"""Apply migration 022 to add business_asset_id to ingested_events."""

import asyncio
from pathlib import Path
from backend.database import get_supabase_admin_client


async def main():
    print("🔄 Applying migration 022: Add business_asset_id to ingested_events\n")

    # Read migration file
    migration_file = Path(__file__).parent.parent / "backend" / "database" / "migrations" / "022_add_business_asset_id_to_ingested_events.sql"

    with open(migration_file, "r") as f:
        sql = f.read()

    print(f"Migration SQL:\n{sql}\n")

    # Get Supabase client
    client = await get_supabase_admin_client()

    # Execute the migration using raw SQL
    try:
        # Supabase Python client doesn't support raw SQL execution directly
        # We need to execute each statement separately
        statements = [
            """
            ALTER TABLE ingested_events
            ADD COLUMN IF NOT EXISTS business_asset_id TEXT REFERENCES business_assets(id)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_ingested_events_business_asset ON ingested_events(business_asset_id)
            """
        ]

        for stmt in statements:
            print(f"Executing: {stmt.strip()[:50]}...")
            # Note: Supabase client doesn't support DDL operations
            # You'll need to run this migration manually in the Supabase SQL editor
            print("⚠️  Cannot execute DDL via Supabase client")
            print("Please run the migration manually in Supabase SQL editor:")
            print(f"\n{sql}\n")
            break

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    print("\n⚠️  Note: Supabase Python client doesn't support DDL operations.")
    print("Please run the migration SQL manually in your Supabase SQL editor:\n")

    migration_file = Path(__file__).parent.parent / "backend" / "database" / "migrations" / "022_add_business_asset_id_to_ingested_events.sql"
    with open(migration_file, "r") as f:
        print(f.read())

    print("\nOr use the Supabase CLI or psycopg2 with direct database connection.")
