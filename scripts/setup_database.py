# scripts/setup_database.py

"""
Initial database setup script.

Creates Supabase storage bucket for generated media.

Usage:
    python scripts/setup_database.py
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()


def setup_storage():
    """Create storage bucket for generated media."""
    print("🗄️  Setting up Supabase storage...\n")

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL or SUPABASE_SERVICE_KEY not set")
        sys.exit(1)

    supabase = create_client(supabase_url, supabase_key)

    # Create storage bucket
    bucket_name = "generated-media"

    try:
        # Try to create bucket
        supabase.storage.create_bucket(
            bucket_name,
            options={"public": True}  # Public bucket for media URLs
        )
        print(f"  ✅ Created storage bucket: {bucket_name}")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"  ℹ️  Storage bucket '{bucket_name}' already exists")
        else:
            print(f"  ❌ Failed to create bucket: {e}")
            sys.exit(1)

    print("\n✅ Storage setup complete!")


if __name__ == "__main__":
    setup_storage()
