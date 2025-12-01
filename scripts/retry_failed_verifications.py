#!/usr/bin/env python3
# scripts/retry_failed_verifications.py

"""
Script to retry verification for posts that failed due to API rate limits.

This script:
1. Finds all verifier_responses with the RESOURCE_EXHAUSTED error
2. Re-runs the verifier agent on each associated post
3. Deletes the old failed verifier_response entry
4. Creates a new verifier_response with the actual result
5. Updates the completed_post verification_status accordingly

Usage:
    python scripts/retry_failed_verifications.py
    python scripts/retry_failed_verifications.py --dry-run
    python scripts/retry_failed_verifications.py --business-asset-id flyeaglesflycommunity
    python scripts/retry_failed_verifications.py --limit 10
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import argparse
from typing import List, Optional
from uuid import UUID

from backend.database import get_supabase_admin_client
from backend.database.repositories.verifier_responses import VerifierResponseRepository
from backend.database.repositories.completed_posts import CompletedPostRepository
from backend.agents.verifier.verifier_agent import VerifierAgent
from backend.models import VerifierResponse
from backend.utils import get_logger

logger = get_logger(__name__)

# The exact error message we're looking for
RATE_LIMIT_ERROR = "Verification failed due to API error: 429 RESOURCE_EXHAUSTED"


async def get_failed_verifications(
    business_asset_id: Optional[str] = None,
    limit: Optional[int] = None
) -> List[dict]:
    """
    Get all verifier responses that failed due to rate limiting.

    Args:
        business_asset_id: Optional filter by business asset
        limit: Maximum number of results

    Returns:
        List of failed verifier response records
    """
    client = await get_supabase_admin_client()

    query = (
        client.table("verifier_responses")
        .select("*")
        .like("reasoning", f"{RATE_LIMIT_ERROR}%")
    )

    if business_asset_id:
        query = query.eq("business_asset_id", business_asset_id)

    if limit:
        query = query.limit(limit)

    query = query.order("created_at", desc=True)

    result = await query.execute()
    return result.data


async def delete_verifier_response(response_id: UUID) -> bool:
    """
    Delete a verifier response by ID (without business_asset_id filter).

    Args:
        response_id: The ID of the verifier response to delete

    Returns:
        True if deleted successfully
    """
    client = await get_supabase_admin_client()
    result = (
        await client.table("verifier_responses")
        .delete()
        .eq("id", str(response_id))
        .execute()
    )
    return len(result.data) > 0


async def retry_verification(
    business_asset_id: str,
    completed_post_id: UUID,
    old_response_id: UUID,
    dry_run: bool = False
) -> dict:
    """
    Retry verification for a single post.

    Args:
        business_asset_id: The business asset ID
        completed_post_id: The post to re-verify
        old_response_id: The old failed response to delete
        dry_run: If True, don't actually make changes

    Returns:
        Result dictionary with status
    """
    result = {
        "completed_post_id": str(completed_post_id),
        "business_asset_id": business_asset_id,
        "old_response_id": str(old_response_id),
        "success": False,
        "new_status": None,
        "error": None
    }

    if dry_run:
        result["success"] = True
        result["new_status"] = "dry_run"
        return result

    try:
        # Initialize the verifier agent
        agent = VerifierAgent(business_asset_id)

        # Delete the old failed response first
        deleted = await delete_verifier_response(old_response_id)
        if not deleted:
            logger.warning(
                "Could not delete old response (may already be deleted)",
                response_id=str(old_response_id)
            )

        # Re-run verification
        new_response = await agent.verify_post(completed_post_id)

        result["success"] = True
        result["new_status"] = "verified" if new_response.is_approved else "rejected"
        result["is_approved"] = new_response.is_approved
        result["reasoning"] = new_response.reasoning[:100] + "..." if len(new_response.reasoning) > 100 else new_response.reasoning

        logger.info(
            "Successfully re-verified post",
            completed_post_id=str(completed_post_id),
            new_status=result["new_status"],
            is_approved=new_response.is_approved
        )

    except Exception as e:
        result["error"] = str(e)
        logger.error(
            "Failed to retry verification",
            completed_post_id=str(completed_post_id),
            error=str(e)
        )

    return result


async def main(
    business_asset_id: Optional[str] = None,
    limit: Optional[int] = None,
    dry_run: bool = False
):
    """
    Main function to retry all failed verifications.

    Args:
        business_asset_id: Optional filter by business asset
        limit: Maximum number of posts to process
        dry_run: If True, only show what would be done
    """
    print("=" * 60)
    print("Retry Failed Verifications Script")
    print("=" * 60)

    if dry_run:
        print("\n[DRY RUN MODE - No changes will be made]\n")

    # Find failed verifications
    print(f"\nSearching for verifications that failed with RESOURCE_EXHAUSTED error...")
    if business_asset_id:
        print(f"  Filtering by business_asset_id: {business_asset_id}")
    if limit:
        print(f"  Limit: {limit}")

    failed_responses = await get_failed_verifications(business_asset_id, limit)

    if not failed_responses:
        print("\nNo failed verifications found matching criteria.")
        return

    print(f"\nFound {len(failed_responses)} failed verification(s) to retry:\n")

    # Group by business asset for display
    by_asset = {}
    for resp in failed_responses:
        asset = resp["business_asset_id"]
        if asset not in by_asset:
            by_asset[asset] = []
        by_asset[asset].append(resp)

    for asset, responses in by_asset.items():
        print(f"  {asset}: {len(responses)} post(s)")
        for resp in responses[:3]:  # Show first 3
            print(f"    - Post: {resp['completed_post_id'][:8]}...")
        if len(responses) > 3:
            print(f"    ... and {len(responses) - 3} more")

    if not dry_run:
        print("\n" + "-" * 60)
        confirm = input("\nProceed with re-verification? (y/N): ")
        if confirm.lower() != 'y':
            print("Aborted.")
            return

    # Process each failed verification
    print("\n" + "=" * 60)
    print("Processing verifications...")
    print("=" * 60 + "\n")

    results = {
        "total": len(failed_responses),
        "success": 0,
        "failed": 0,
        "approved": 0,
        "rejected": 0
    }

    for i, resp in enumerate(failed_responses, 1):
        post_id = resp["completed_post_id"]
        asset_id = resp["business_asset_id"]
        response_id = resp["id"]

        print(f"[{i}/{len(failed_responses)}] Processing post {post_id[:8]}... ({asset_id})")

        result = await retry_verification(
            business_asset_id=asset_id,
            completed_post_id=UUID(post_id),
            old_response_id=UUID(response_id),
            dry_run=dry_run
        )

        if result["success"]:
            results["success"] += 1
            if result.get("is_approved"):
                results["approved"] += 1
                print(f"    Approved")
            elif result["new_status"] == "dry_run":
                print(f"    [Would be retried]")
            else:
                results["rejected"] += 1
                print(f"    Rejected")
        else:
            results["failed"] += 1
            print(f"    FAILED: {result.get('error', 'Unknown error')}")

        # Small delay between requests to avoid rate limiting again
        if not dry_run and i < len(failed_responses):
            await asyncio.sleep(1)

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"\n  Total processed: {results['total']}")
    print(f"  Successful:      {results['success']}")
    print(f"  Failed:          {results['failed']}")
    if not dry_run:
        print(f"\n  New verifications:")
        print(f"    Approved: {results['approved']}")
        print(f"    Rejected: {results['rejected']}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Retry verification for posts that failed due to API rate limits",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--business-asset-id",
        type=str,
        help="Only process posts for this business asset"
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of posts to process"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )

    args = parser.parse_args()

    asyncio.run(main(
        business_asset_id=args.business_asset_id,
        limit=args.limit,
        dry_run=args.dry_run
    ))
