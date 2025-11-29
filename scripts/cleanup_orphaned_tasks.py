#!/usr/bin/env python3
"""
Script to find and clean up orphaned content creation tasks.

Orphaned tasks are those that reference content seeds that no longer exist.
This can happen if seeds are deleted while tasks are still pending.
"""

import asyncio
from backend.database.repositories.content_creation_tasks import ContentCreationTaskRepository
from backend.database.repositories.trend_seeds import TrendSeedsRepository
from backend.database.repositories.news_event_seeds import NewsEventSeedRepository
from backend.database.repositories.ungrounded_seeds import UngroundedSeedRepository


async def find_and_fix_orphaned_tasks(business_asset_id: str, fix: bool = False):
    """
    Find orphaned tasks and optionally mark them as failed.

    Args:
        business_asset_id: The business asset ID to check
        fix: If True, mark orphaned tasks as failed
    """
    tasks_repo = ContentCreationTaskRepository()
    trend_repo = TrendSeedsRepository()
    news_repo = NewsEventSeedRepository()
    ungrounded_repo = UngroundedSeedRepository()

    # Get all pending tasks
    tasks = await tasks_repo.get_pending_tasks(business_asset_id, limit=1000)

    print(f"Checking {len(tasks)} pending tasks for {business_asset_id}...")

    orphaned = []
    for task in tasks:
        seed_id = str(task.content_seed_id)
        seed_type = task.content_seed_type

        # Check if seed exists
        seed = None
        if seed_type == 'trend':
            seed = await trend_repo.get_by_id(business_asset_id, seed_id)
        elif seed_type == 'news_event':
            seed = await news_repo.get_by_id(business_asset_id, seed_id)
        elif seed_type == 'ungrounded':
            seed = await ungrounded_repo.get_by_id(business_asset_id, seed_id)

        if not seed:
            orphaned.append({
                'task_id': str(task.id),
                'seed_type': seed_type,
                'seed_id': seed_id,
                'created_at': task.created_at
            })
            print(f"  [ORPHANED] Task {task.id}")
            print(f"    - Type: {seed_type}")
            print(f"    - Missing seed ID: {seed_id}")
            print(f"    - Created: {task.created_at}")

            if fix:
                await tasks_repo.update(
                    business_asset_id,
                    str(task.id),
                    {
                        'status': 'failed',
                        'error_message': f'Content seed {seed_id} ({seed_type}) no longer exists'
                    }
                )
                print(f"    - ✅ Marked as failed")

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total pending tasks: {len(tasks)}")
    print(f"  Orphaned tasks: {len(orphaned)}")
    if orphaned and fix:
        print(f"  Fixed: {len(orphaned)}")
    elif orphaned and not fix:
        print(f"  Run with --fix flag to mark orphaned tasks as failed")
    print(f"{'='*60}")

    return orphaned


if __name__ == "__main__":
    import sys

    # Parse arguments
    business_asset_id = sys.argv[1] if len(sys.argv) > 1 else 'penndailybuzz'
    fix = '--fix' in sys.argv

    print(f"Orphaned Task Cleanup Tool")
    print(f"Business Asset: {business_asset_id}")
    print(f"Fix mode: {'ENABLED' if fix else 'DISABLED (dry run)'}")
    print(f"{'='*60}\n")

    asyncio.run(find_and_fix_orphaned_tasks(business_asset_id, fix))
