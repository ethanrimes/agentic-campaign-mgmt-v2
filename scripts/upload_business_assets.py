#!/usr/bin/env python3
# scripts/upload_business_assets.py

"""
Script to upload business asset credentials to Supabase.

This script reads business asset credentials from environment variables,
encrypts the access tokens using ENCRYPTION_KEY, and uploads them to
the business_assets table in Supabase.

Usage:
    python scripts/upload_business_assets.py --asset-id penndailybuzz
    python scripts/upload_business_assets.py --asset-id eaglesnationfanhuddle
    python scripts/upload_business_assets.py --all  # Upload all from JSON file

Environment variables required for each asset:
    {ASSET_ID}_FACEBOOK_PAGE_ID
    {ASSET_ID}_APP_USERS_INSTAGRAM_ACCOUNT_ID
    {ASSET_ID}_FACEBOOK_PAGE_ACCESS_TOKEN
    {ASSET_ID}_INSTAGRAM_PAGE_ACCESS_TOKEN
    {ASSET_ID}_TARGET_AUDIENCE

Example:
    PENNDAILYBUZZ_FACEBOOK_PAGE_ID=123456789
    PENNDAILYBUZZ_APP_USERS_INSTAGRAM_ACCOUNT_ID=987654321
    PENNDAILYBUZZ_FACEBOOK_PAGE_ACCESS_TOKEN=EAAxxxxx
    PENNDAILYBUZZ_INSTAGRAM_PAGE_ACCESS_TOKEN=IGQxxxxx
    PENNDAILYBUZZ_TARGET_AUDIENCE="College students at UPenn interested in campus news"
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import json
import argparse
from typing import Dict, Optional
from backend.database.repositories.business_assets import BusinessAssetRepository
from backend.models.business_asset import BusinessAssetCreate, BusinessAssetUpdate
from backend.utils import get_logger

logger = get_logger(__name__)


# Asset ID to display name mapping
ASSET_NAMES = {
    "penndailybuzz": "Penn Daily Buzz",
    "eaglesnationfanhuddle": "Eagles Nation Fan Huddle",
    "flyeaglesflycommunity": "Fly Eagles Fly Community",
    "oceankindnesscollective": "Ocean Kindness Collective",
    "blueplanetbeachstewards": "Blue Planet Beach Stewards",
    "airesearchinsightslab": "AI Research Insights Lab",
    "aifirstnewsreport": "AI First News Report",
}


def get_credentials_from_env(asset_id: str) -> Optional[Dict[str, str]]:
    """
    Get credentials for a business asset from environment variables.

    Environment variable format: {ASSET_ID_UPPER}_{FIELD_NAME}
    Example: PENNDAILYBUZZ_FACEBOOK_PAGE_ID

    Args:
        asset_id: The business asset ID (lowercase)

    Returns:
        Dictionary with credentials or None if any required field is missing
    """
    asset_id_upper = asset_id.upper()

    required_fields = {
        "facebook_page_id": f"{asset_id_upper}_FACEBOOK_PAGE_ID",
        "app_users_instagram_account_id": f"{asset_id_upper}_APP_USERS_INSTAGRAM_ACCOUNT_ID",
        "facebook_page_access_token": f"{asset_id_upper}_FACEBOOK_PAGE_ACCESS_TOKEN",
        "instagram_page_access_token": f"{asset_id_upper}_INSTAGRAM_PAGE_ACCESS_TOKEN",
        "target_audience": f"{asset_id_upper}_TARGET_AUDIENCE",
    }

    credentials = {}
    missing_fields = []

    for field_name, env_var in required_fields.items():
        value = os.getenv(env_var)
        if not value:
            missing_fields.append(env_var)
        else:
            credentials[field_name] = value

    if missing_fields:
        logger.error(
            f"Missing environment variables for {asset_id}",
            missing=missing_fields,
        )
        return None

    return credentials


def upload_business_asset(
    asset_id: str,
    credentials: Dict[str, str],
    update_if_exists: bool = False
) -> bool:
    """
    Upload or update a business asset.

    Args:
        asset_id: The business asset ID
        credentials: Dictionary with credential fields
        update_if_exists: If True, update existing asset; if False, skip if exists

    Returns:
        True if successful, False otherwise
    """
    repo = BusinessAssetRepository()

    # Check if asset already exists
    existing = repo.get_by_id(asset_id)

    if existing:
        if not update_if_exists:
            logger.info(f"Business asset already exists: {asset_id} (use --update to overwrite)")
            return True

        logger.info(f"Updating existing business asset: {asset_id}")
        update = BusinessAssetUpdate(
            name=ASSET_NAMES.get(asset_id, asset_id.title()),
            **credentials
        )
        result = repo.update(asset_id, update)
        if result:
            logger.info(f"✓ Successfully updated business asset: {asset_id}")
            return True
        else:
            logger.error(f"✗ Failed to update business asset: {asset_id}")
            return False
    else:
        logger.info(f"Creating new business asset: {asset_id}")
        create = BusinessAssetCreate(
            id=asset_id,
            name=ASSET_NAMES.get(asset_id, asset_id.title()),
            **credentials,
            is_active=True,
        )
        try:
            repo.create(create)
            logger.info(f"✓ Successfully created business asset: {asset_id}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to create business asset: {asset_id}", error=str(e))
            return False


def upload_from_json(json_file: str, update_if_exists: bool = False) -> None:
    """
    Upload multiple business assets from a JSON file.

    JSON format:
    {
        "asset_id": {
            "facebook_page_id": "...",
            "app_users_instagram_account_id": "...",
            "facebook_page_access_token": "...",
            "instagram_page_access_token": "...",
            "target_audience": "..."
        },
        ...
    }

    Args:
        json_file: Path to JSON file
        update_if_exists: Whether to update existing assets
    """
    try:
        with open(json_file, 'r') as f:
            assets_data = json.load(f)

        success_count = 0
        fail_count = 0

        for asset_id, credentials in assets_data.items():
            if upload_business_asset(asset_id, credentials, update_if_exists):
                success_count += 1
            else:
                fail_count += 1

        logger.info(
            f"Upload complete: {success_count} succeeded, {fail_count} failed"
        )

    except FileNotFoundError:
        logger.error(f"JSON file not found: {json_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Upload business asset credentials to Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--asset-id",
        type=str,
        help="Business asset ID to upload (e.g., penndailybuzz)",
    )

    parser.add_argument(
        "--from-json",
        type=str,
        metavar="FILE",
        help="Upload multiple assets from JSON file",
    )

    parser.add_argument(
        "--update",
        action="store_true",
        help="Update existing assets instead of skipping them",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all configured asset IDs",
    )

    args = parser.parse_args()

    # List assets
    if args.list:
        print("Configured business asset IDs:")
        for asset_id, name in ASSET_NAMES.items():
            print(f"  - {asset_id:30} ({name})")
        return

    # Validate arguments
    if not args.asset_id and not args.from_json:
        parser.error("Either --asset-id or --from-json must be specified")

    # Upload from JSON
    if args.from_json:
        upload_from_json(args.from_json, args.update)
        return

    # Upload single asset from environment
    if args.asset_id:
        asset_id = args.asset_id.lower()

        logger.info(f"Uploading business asset: {asset_id}")

        credentials = get_credentials_from_env(asset_id)
        if not credentials:
            logger.error(
                f"Cannot upload {asset_id}: missing required environment variables"
            )
            sys.exit(1)

        if upload_business_asset(asset_id, credentials, args.update):
            logger.info("Upload successful!")
        else:
            logger.error("Upload failed!")
            sys.exit(1)


if __name__ == "__main__":
    main()
