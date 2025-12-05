#!/usr/bin/env python3
# scripts/override_verification.py

"""
Script to manually override a rejected verifier report.

This script:
1. Takes a completed_post_id of a rejected post
2. Updates the verification_status to "manually_overridden"
3. This makes the post eligible for publishing on social media platforms

Usage:
    python scripts/override_verification.py <post_id>
    python scripts/override_verification.py <post_id> --dry-run
    python scripts/override_verification.py --list-rejected [--business-asset-id <id>]

Examples:
    # Override a specific post
    python scripts/override_verification.py abc123-def456-...

    # List all rejected posts
    python scripts/override_verification.py --list-rejected

    # List rejected posts for a specific business asset
    python scripts/override_verification.py --list-rejected --business-asset-id penndailybuzz
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import argparse
from typing import Optional
from uuid import UUID

from backend.database import get_supabase_admin_client
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.database.repositories.verifier_responses import VerifierResponseRepository
from backend.utils import get_logger

logger = get_logger(__name__)


async def list_rejected_posts(business_asset_id: Optional[str] = None, limit: int = 50):
    """
    List all rejected posts that could be overridden.

    Args:
        business_asset_id: Optional filter by business asset
        limit: Maximum number of results
    """
    client = await get_supabase_admin_client()

    query = (
        client.table("completed_posts")
        .select("id, platform, post_type, text, verification_status, created_at, business_asset_id")
        .eq("verification_status", "rejected")
        .eq("status", "pending")
        .order("created_at", desc=True)
        .limit(limit)
    )

    if business_asset_id:
        query = query.eq("business_asset_id", business_asset_id)

    result = await query.execute()
    return result.data


async def get_post_details(post_id: UUID) -> Optional[dict]:
    """
    Get details of a specific post.

    Args:
        post_id: The UUID of the post

    Returns:
        Post data or None if not found
    """
    client = await get_supabase_admin_client()
    result = (
        await client.table("completed_posts")
        .select("*")
        .eq("id", str(post_id))
        .execute()
    )

    if result.data:
        return result.data[0]
    return None


async def get_verifier_response(post_id: UUID) -> Optional[dict]:
    """
    Get the most recent verifier response for a post.

    Args:
        post_id: The UUID of the completed post

    Returns:
        Verifier response data or None if not found
    """
    client = await get_supabase_admin_client()
    result = (
        await client.table("verifier_responses")
        .select("*")
        .eq("completed_post_id", str(post_id))
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if result.data:
        return result.data[0]
    return None


async def override_verification(
    post_id: UUID,
    dry_run: bool = False
) -> dict:
    """
    Override a rejected verification, making the post eligible for publishing.

    Args:
        post_id: The UUID of the completed post to override
        dry_run: If True, only show what would be done

    Returns:
        Result dictionary with status
    """
    result = {
        "post_id": str(post_id),
        "success": False,
        "message": None,
        "old_status": None,
        "new_status": "manually_overridden"
    }

    # Get the post
    post = await get_post_details(post_id)

    if not post:
        result["message"] = f"Post not found: {post_id}"
        return result

    result["business_asset_id"] = post["business_asset_id"]
    result["platform"] = post["platform"]
    result["post_type"] = post["post_type"]
    result["old_status"] = post["verification_status"]

    # Check if the post is actually rejected
    if post["verification_status"] != "rejected":
        result["message"] = f"Post is not rejected (current status: {post['verification_status']})"
        return result

    # Check if the post is pending (not already published)
    if post["status"] != "pending":
        result["message"] = f"Post is not pending (current status: {post['status']})"
        return result

    if dry_run:
        result["success"] = True
        result["message"] = "Would override verification (dry run)"
        return result

    # Update the verification status
    client = await get_supabase_admin_client()
    update_result = (
        await client.table("completed_posts")
        .update({"verification_status": "manually_overridden"})
        .eq("id", str(post_id))
        .execute()
    )

    if update_result.data:
        result["success"] = True
        result["message"] = "Verification status updated to 'manually_overridden'"
        logger.info(
            "Verification overridden",
            post_id=str(post_id),
            business_asset_id=post["business_asset_id"],
            platform=post["platform"]
        )
    else:
        result["message"] = "Failed to update verification status"
        logger.error(
            "Failed to override verification",
            post_id=str(post_id)
        )

    return result


async def main_list(business_asset_id: Optional[str] = None, limit: int = 50):
    """List rejected posts that can be overridden."""
    print("=" * 70)
    print("Rejected Posts Available for Override")
    print("=" * 70)

    if business_asset_id:
        print(f"\nFiltering by business_asset_id: {business_asset_id}")

    posts = await list_rejected_posts(business_asset_id, limit)

    if not posts:
        print("\nNo rejected posts found.")
        return

    print(f"\nFound {len(posts)} rejected post(s):\n")

    # Group by business asset
    by_asset = {}
    for post in posts:
        asset = post["business_asset_id"]
        if asset not in by_asset:
            by_asset[asset] = []
        by_asset[asset].append(post)

    for asset, asset_posts in by_asset.items():
        print(f"\n[{asset}]")
        print("-" * 60)

        for post in asset_posts:
            post_id = post["id"]
            platform = post["platform"]
            post_type = post["post_type"]
            text_preview = post["text"][:60] + "..." if len(post["text"]) > 60 else post["text"]
            text_preview = text_preview.replace("\n", " ")

            print(f"\n  ID: {post_id}")
            print(f"  Platform: {platform} | Type: {post_type}")
            print(f"  Text: \"{text_preview}\"")

            # Get verifier response
            verifier = await get_verifier_response(UUID(post_id))
            if verifier:
                print(f"  Reason: {verifier['reasoning'][:80]}...")
                if verifier.get("issues_found"):
                    print(f"  Issues: {', '.join(verifier['issues_found'][:3])}")

    print("\n" + "=" * 70)
    print("\nTo override a post, run:")
    print("  python scripts/override_verification.py <post_id>")
    print()


async def main_override(post_id: str, dry_run: bool = False):
    """Override a specific post's verification."""
    print("=" * 70)
    print("Override Verification")
    print("=" * 70)

    if dry_run:
        print("\n[DRY RUN MODE - No changes will be made]\n")

    try:
        post_uuid = UUID(post_id)
    except ValueError:
        print(f"\nError: Invalid UUID format: {post_id}")
        return

    # Get post details
    post = await get_post_details(post_uuid)

    if not post:
        print(f"\nError: Post not found: {post_id}")
        return

    print(f"\nPost Details:")
    print(f"  ID:                  {post['id']}")
    print(f"  Business Asset:      {post['business_asset_id']}")
    print(f"  Platform:            {post['platform']}")
    print(f"  Post Type:           {post['post_type']}")
    print(f"  Current Status:      {post['status']}")
    print(f"  Verification Status: {post['verification_status']}")

    text_preview = post["text"][:100] + "..." if len(post["text"]) > 100 else post["text"]
    print(f"  Text Preview:        \"{text_preview}\"")

    # Get verifier response
    verifier = await get_verifier_response(post_uuid)
    if verifier:
        print(f"\nVerifier Response:")
        print(f"  Model:     {verifier['model']}")
        print(f"  Approved:  {verifier['is_approved']}")
        print(f"  Reasoning: {verifier['reasoning'][:150]}...")
        if verifier.get("issues_found"):
            print(f"  Issues:    {verifier['issues_found']}")

    if post["verification_status"] != "rejected":
        print(f"\nError: Post is not rejected (status: {post['verification_status']})")
        return

    if post["status"] != "pending":
        print(f"\nError: Post is not pending (status: {post['status']})")
        return

    # Confirmation
    if not dry_run:
        print("\n" + "-" * 70)
        print("\nWARNING: This will mark the post as 'manually_overridden' and")
        print("         make it eligible for publishing on social media.")
        confirm = input("\nProceed with override? (y/N): ")
        if confirm.lower() != 'y':
            print("Aborted.")
            return

    # Perform override
    result = await override_verification(post_uuid, dry_run)

    print("\n" + "=" * 70)
    if result["success"]:
        print(f"\nSUCCESS: {result['message']}")
        print(f"\n  Previous status: {result['old_status']}")
        print(f"  New status:      {result['new_status']}")
        print(f"\n  The post is now eligible for publishing.")
    else:
        print(f"\nFAILED: {result['message']}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Manually override a rejected verifier report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "post_id",
        type=str,
        nargs="?",
        help="UUID of the completed post to override"
    )

    parser.add_argument(
        "--list-rejected",
        action="store_true",
        help="List all rejected posts that can be overridden"
    )

    parser.add_argument(
        "--business-asset-id",
        type=str,
        help="Filter by business asset ID (for --list-rejected)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of posts to list (default: 50)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )

    args = parser.parse_args()

    if args.list_rejected:
        asyncio.run(main_list(args.business_asset_id, args.limit))
    elif args.post_id:
        asyncio.run(main_override(args.post_id, args.dry_run))
    else:
        parser.print_help()
        print("\nError: Either provide a post_id or use --list-rejected")
