#!/usr/bin/env python3
"""
Script to configure read-only permissions for the Supabase anonymous role.
This ensures that the NEXT_PUBLIC_SUPABASE_ANON_KEY can only read data, not write.
"""

import os
import sys
from pathlib import Path

# Try to import psycopg2
try:
    import psycopg2
    from psycopg2 import sql
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

# Load environment variables from .env.local
env_path = Path(__file__).parent.parent / "frontend" / ".env.local"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Tables to configure
TABLES = [
    'completed_posts',
    'content_creation_tasks',
    'ingested_event_sources',
    'ingested_events',
    'insight_reports',
    'media',
    'news_event_seed_sources',
    'news_event_seeds',
    'sources',
    'trend_seeds',
    'ungrounded_seeds'
]

def get_database_url():
    """Get database connection URL from environment or prompt user."""
    db_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")

    if not db_url:
        print("\nDatabase connection string not found in environment.")
        print("\nTo get your connection string:")
        print("1. Go to Supabase Dashboard > Project Settings > Database")
        print("2. Copy the 'Connection string' (URI format)")
        print("3. Make sure to replace [YOUR-PASSWORD] with your actual database password")
        print("\nOr set DATABASE_URL in your environment/.env.local file")

        db_url = input("\nEnter your database connection string (or press Enter to see alternative methods): ").strip()

    return db_url

def configure_with_psycopg2(db_url):
    """Configure RLS policies using psycopg2."""
    print("\nConnecting to database...")

    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = False
        cursor = conn.cursor()

        print("Configuring read-only permissions for anonymous role...")
        print("=" * 60)

        for table_name in TABLES:
            try:
                # Enable RLS
                cursor.execute(sql.SQL("ALTER TABLE public.{} ENABLE ROW LEVEL SECURITY;").format(
                    sql.Identifier(table_name)
                ))

                # Drop existing anon policies
                cursor.execute(sql.SQL("DROP POLICY IF EXISTS {policy} ON public.{table};").format(
                    policy=sql.Identifier("anon_read_only"),
                    table=sql.Identifier(table_name)
                ))
                cursor.execute(sql.SQL("DROP POLICY IF EXISTS {policy} ON public.{table};").format(
                    policy=sql.Identifier("anon_select"),
                    table=sql.Identifier(table_name)
                ))

                # Create read-only policy
                cursor.execute(sql.SQL("""
                    CREATE POLICY {policy}
                    ON public.{table}
                    FOR SELECT
                    TO anon
                    USING (true);
                """).format(
                    policy=sql.Identifier("anon_read_only"),
                    table=sql.Identifier(table_name)
                ))

                print(f"✓ Configured read-only access for table: {table_name}")

            except Exception as e:
                print(f"✗ Error configuring {table_name}: {e}")
                conn.rollback()
                raise

        # Commit all changes
        conn.commit()

        print("\n" + "=" * 60)
        print("SUCCESS! All tables are now READ-ONLY for the anonymous key")
        print("=" * 60)

        # Verify configuration
        print("\nVerifying configuration...")
        cursor.execute("""
            SELECT tablename, rowsecurity as "RLS Enabled"
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename = ANY(%s)
            ORDER BY tablename;
        """, (TABLES,))

        print("\nTable Security Status:")
        for row in cursor.fetchall():
            status = "✓ Enabled" if row[1] else "✗ Disabled"
            print(f"  {row[0]}: {status}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

def show_manual_instructions():
    """Show manual instructions for setting up RLS."""
    sql_script_path = Path(__file__).parent / "setup_read_only_anon_policies.sql"

    print("\n" + "=" * 60)
    print("MANUAL SETUP INSTRUCTIONS")
    print("=" * 60)

    print("\nOption 1: Use the Supabase SQL Editor (RECOMMENDED)")
    print("-" * 60)
    print("1. Go to your Supabase Dashboard")
    print("2. Navigate to: SQL Editor (left sidebar)")
    print("3. Click 'New query'")
    print(f"4. Copy the contents of: {sql_script_path}")
    print("5. Paste into the SQL Editor")
    print("6. Click 'Run' or press Cmd/Ctrl + Enter")

    print("\nOption 2: Use psql command line")
    print("-" * 60)
    print("1. Install psycopg2: pip install psycopg2-binary")
    print("2. Run this script again")

    print("\nOption 3: Use psql directly")
    print("-" * 60)
    print("1. Get your database connection string from Supabase Dashboard")
    print("2. Run the following command:")
    print(f"   psql 'YOUR_CONNECTION_STRING' -f {sql_script_path}")

def main():
    print("=" * 60)
    print("Supabase Anonymous Role - Read-Only Configuration")
    print("=" * 60)

    if not HAS_PSYCOPG2:
        print("\npsycopg2 not installed. To auto-execute, install it with:")
        print("  pip install psycopg2-binary")
        show_manual_instructions()
        return

    db_url = get_database_url()

    if not db_url:
        show_manual_instructions()
        return

    configure_with_psycopg2(db_url)

if __name__ == "__main__":
    main()
