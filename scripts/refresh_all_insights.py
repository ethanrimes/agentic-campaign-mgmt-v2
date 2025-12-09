#!/usr/bin/env python3
"""
Refresh insights for all business assets.

This script fetches the latest engagement metrics for all posts across all
configured business assets. It updates both account-level and post-level
insights for Facebook and Instagram.

Usage:
    # Refresh all business assets (default: from assets.json)
    python scripts/refresh_all_insights.py

    # Refresh specific business assets
    python scripts/refresh_all_insights.py --assets penndailybuzz airesearchinsightslab

    # Only refresh post-level insights (skip account insights)
    python scripts/refresh_all_insights.py --posts-only

    # Only refresh account-level insights (skip post insights)
    python scripts/refresh_all_insights.py --accounts-only

    # Set custom limits
    python scripts/refresh_all_insights.py --limit 100 --days-back 90

    # Dry run (show what would be refreshed without actually doing it)
    python scripts/refresh_all_insights.py --dry-run
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.utils import get_logger
from backend.services.insights_fetcher import (
    fetch_account_insights,
    fetch_post_insights,
    fetch_all_insights,
)
from backend.config.settings import settings

logger = get_logger(__name__)

# Default list of all business assets
DEFAULT_ASSETS = [
    "penndailybuzz",
    "eaglesnationfanhuddle",
    "flyeaglesflycommunity",
    "oceankindnesscollective",
    "blueplanetbeachstewards",
    "airesearchinsightslab",
    "aifirstnewsreport",
]


def load_assets_from_file() -> List[str]:
    """Load business asset IDs from assets.json."""
    assets_path = Path(__file__).parent.parent / "assets.json"
    if assets_path.exists():
        with open(assets_path) as f:
            assets_data = json.load(f)
            return list(assets_data.keys())
    return DEFAULT_ASSETS


async def refresh_single_asset(
    business_asset_id: str,
    fetch_accounts: bool = True,
    fetch_posts: bool = True,
    limit: int = None,
    days_back: int = None,
) -> Dict[str, Any]:
    """
    Refresh insights for a single business asset.

    Args:
        business_asset_id: The business asset ID
        fetch_accounts: Whether to fetch account-level insights
        fetch_posts: Whether to fetch post-level insights
        limit: Max posts to fetch per platform
        days_back: Only fetch posts from last N days

    Returns:
        Dictionary with results and any errors
    """
    result = {
        "business_asset_id": business_asset_id,
        "account_insights": None,
        "post_insights": None,
        "errors": [],
        "success": True,
    }

    try:
        # Fetch account insights
        if fetch_accounts:
            try:
                account_result = await fetch_account_insights(business_asset_id)
                result["account_insights"] = {
                    "facebook": account_result.get("facebook") is not None,
                    "instagram": account_result.get("instagram") is not None,
                }
                if account_result.get("errors"):
                    result["errors"].extend(account_result["errors"])
            except Exception as e:
                error_msg = f"Account insights error: {str(e)}"
                result["errors"].append(error_msg)
                logger.error(error_msg, business_asset_id=business_asset_id)

        # Fetch post insights
        if fetch_posts:
            try:
                post_result = await fetch_post_insights(
                    business_asset_id,
                    limit=limit or settings.insights_post_limit,
                    days_back=days_back or settings.insights_post_days_back,
                )
                result["post_insights"] = {
                    "facebook_posts": post_result.get("facebook_posts_fetched", 0),
                    "facebook_videos": post_result.get("facebook_videos_fetched", 0),
                    "instagram_media": post_result.get("instagram_media_fetched", 0),
                }
                if post_result.get("errors"):
                    result["errors"].extend(post_result["errors"])
            except Exception as e:
                error_msg = f"Post insights error: {str(e)}"
                result["errors"].append(error_msg)
                logger.error(error_msg, business_asset_id=business_asset_id)

    except Exception as e:
        result["success"] = False
        result["errors"].append(f"Fatal error: {str(e)}")
        logger.error("Failed to refresh insights", business_asset_id=business_asset_id, error=str(e))

    return result


async def refresh_all_assets(
    assets: List[str],
    fetch_accounts: bool = True,
    fetch_posts: bool = True,
    limit: int = None,
    days_back: int = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Refresh insights for all specified business assets.

    Args:
        assets: List of business asset IDs to refresh
        fetch_accounts: Whether to fetch account-level insights
        fetch_posts: Whether to fetch post-level insights
        limit: Max posts to fetch per platform
        days_back: Only fetch posts from last N days
        dry_run: If True, just print what would be done without doing it

    Returns:
        Dictionary with overall results
    """
    start_time = datetime.now()

    print(f"\n{'='*60}")
    print(f"INSIGHTS REFRESH - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    print(f"\nAssets to refresh: {len(assets)}")
    print(f"Fetch accounts: {fetch_accounts}")
    print(f"Fetch posts: {fetch_posts}")
    print(f"Post limit: {limit or settings.insights_post_limit}")
    print(f"Days back: {days_back or settings.insights_post_days_back}")
    print(f"Dry run: {dry_run}")
    print()

    if dry_run:
        print("DRY RUN - No actual API calls will be made\n")
        for asset in assets:
            print(f"  Would refresh: {asset}")
        print(f"\nDry run complete. {len(assets)} assets would be refreshed.")
        return {"dry_run": True, "assets": assets}

    results = {
        "total_assets": len(assets),
        "successful": 0,
        "failed": 0,
        "total_facebook_posts": 0,
        "total_facebook_videos": 0,
        "total_instagram_media": 0,
        "errors": [],
        "asset_results": {},
    }

    for i, asset in enumerate(assets, 1):
        print(f"[{i}/{len(assets)}] Refreshing {asset}...")

        try:
            asset_result = await refresh_single_asset(
                asset,
                fetch_accounts=fetch_accounts,
                fetch_posts=fetch_posts,
                limit=limit,
                days_back=days_back,
            )

            results["asset_results"][asset] = asset_result

            if asset_result["success"]:
                results["successful"] += 1

                # Aggregate counts
                if asset_result.get("post_insights"):
                    results["total_facebook_posts"] += asset_result["post_insights"].get("facebook_posts", 0)
                    results["total_facebook_videos"] += asset_result["post_insights"].get("facebook_videos", 0)
                    results["total_instagram_media"] += asset_result["post_insights"].get("instagram_media", 0)

                # Print success info
                post_info = asset_result.get("post_insights", {})
                fb_posts = post_info.get("facebook_posts", 0)
                fb_videos = post_info.get("facebook_videos", 0)
                ig_media = post_info.get("instagram_media", 0)
                print(f"    ✓ FB posts: {fb_posts}, FB videos: {fb_videos}, IG media: {ig_media}")
            else:
                results["failed"] += 1
                print(f"    ✗ Failed")

            # Show any errors
            if asset_result.get("errors"):
                results["errors"].extend([(asset, e) for e in asset_result["errors"]])
                for error in asset_result["errors"][:2]:  # Show first 2 errors
                    print(f"    ⚠ {error[:80]}...")

        except Exception as e:
            results["failed"] += 1
            results["errors"].append((asset, str(e)))
            print(f"    ✗ Error: {str(e)[:80]}...")

        # Small delay between assets to avoid rate limiting
        if i < len(assets):
            await asyncio.sleep(1)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Duration: {duration:.1f} seconds")
    print(f"Assets processed: {results['total_assets']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"\nTotal insights fetched:")
    print(f"  Facebook posts: {results['total_facebook_posts']}")
    print(f"  Facebook videos: {results['total_facebook_videos']}")
    print(f"  Instagram media: {results['total_instagram_media']}")

    if results["errors"]:
        print(f"\nErrors encountered: {len(results['errors'])}")
        for asset, error in results["errors"][:5]:  # Show first 5 errors
            print(f"  [{asset}] {error[:60]}...")

    print(f"\n{'='*60}\n")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Refresh insights for all business assets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--assets",
        nargs="+",
        help="Specific business asset IDs to refresh (default: all from assets.json)",
    )

    parser.add_argument(
        "--accounts-only",
        action="store_true",
        help="Only refresh account-level insights (skip posts)",
    )

    parser.add_argument(
        "--posts-only",
        action="store_true",
        help="Only refresh post-level insights (skip accounts)",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=f"Max posts to fetch per platform (default: {settings.insights_post_limit})",
    )

    parser.add_argument(
        "--days-back",
        type=int,
        default=None,
        help=f"Only fetch posts from last N days (default: {settings.insights_post_days_back})",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be refreshed without actually doing it",
    )

    args = parser.parse_args()

    # Determine which assets to refresh
    if args.assets:
        assets = args.assets
    else:
        assets = load_assets_from_file()

    # Determine what to fetch
    fetch_accounts = not args.posts_only
    fetch_posts = not args.accounts_only

    # Validate that we're fetching something
    if not fetch_accounts and not fetch_posts:
        print("Error: Cannot use both --accounts-only and --posts-only together")
        sys.exit(1)

    # Run the refresh
    results = asyncio.run(
        refresh_all_assets(
            assets=assets,
            fetch_accounts=fetch_accounts,
            fetch_posts=fetch_posts,
            limit=args.limit,
            days_back=args.days_back,
            dry_run=args.dry_run,
        )
    )

    # Exit with error code if any failures
    if results.get("failed", 0) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
