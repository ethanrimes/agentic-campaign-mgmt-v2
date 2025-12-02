# backend/agents/planner/validator.py

"""Planner output validation against guardrails.

Uses unified format-based validation (image_posts, video_posts, text_only_posts)
where each image/video post creates both an Instagram and Facebook post.
"""

from typing import Dict, Any, List, Tuple
from backend.config.guardrails_config import GuardrailsConfig
from backend.utils import get_logger

logger = get_logger(__name__)

class PlannerValidator:
    """
    Validates planner output against guardrails.

    Ensures plans meet all min/max constraints before execution.
    Uses unified format counting:
    - Each image_post creates 2 posts (IG + FB)
    - Each video_post creates 2 posts (IG + FB)
    - Each text_only_post creates 1 post (FB only)
    """

    @staticmethod
    def validate(plan: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a planner output against guardrails.

        Args:
            plan: Dictionary with 'allocations', 'reasoning', 'week_start_date'

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Extract allocations
        allocations = plan.get("allocations", [])

        if not allocations:
            errors.append("Plan contains no allocations")
            return False, errors

        # Calculate totals
        totals = PlannerValidator._calculate_totals(allocations)
        guardrails_config = GuardrailsConfig()

        # Validate total posts (counting both platforms)
        if totals["posts"] < guardrails_config.min_posts_per_week:
            errors.append(
                f"Total posts ({totals['posts']}) is below minimum ({guardrails_config.min_posts_per_week})"
            )
        if totals["posts"] > guardrails_config.max_posts_per_week:
            errors.append(
                f"Total posts ({totals['posts']}) exceeds maximum ({guardrails_config.max_posts_per_week})"
            )

        # Validate total seeds
        num_seeds = len(allocations)
        if num_seeds < guardrails_config.min_content_seeds_per_week:
            errors.append(
                f"Number of content seeds ({num_seeds}) is below minimum ({guardrails_config.min_content_seeds_per_week})"
            )
        if num_seeds > guardrails_config.max_content_seeds_per_week:
            errors.append(
                f"Number of content seeds ({num_seeds}) exceeds maximum ({guardrails_config.max_content_seeds_per_week})"
            )

        # Validate total video posts (post units, not platform count)
        if totals["video_posts"] < guardrails_config.min_videos_per_week:
            errors.append(
                f"Total video posts ({totals['video_posts']}) is below minimum ({guardrails_config.min_videos_per_week})"
            )
        if totals["video_posts"] > guardrails_config.max_videos_per_week:
            errors.append(
                f"Total video posts ({totals['video_posts']}) exceeds maximum ({guardrails_config.max_videos_per_week})"
            )

        # Validate total image posts (post units, not platform count)
        if totals["image_posts"] < guardrails_config.min_images_per_week:
            errors.append(
                f"Total image posts ({totals['image_posts']}) is below minimum ({guardrails_config.min_images_per_week})"
            )
        if totals["image_posts"] > guardrails_config.max_images_per_week:
            errors.append(
                f"Total image posts ({totals['image_posts']}) exceeds maximum ({guardrails_config.max_images_per_week})"
            )

        # Validate individual allocations
        for i, allocation in enumerate(allocations):
            allocation_errors = PlannerValidator._validate_allocation(allocation, i)
            errors.extend(allocation_errors)

        is_valid = len(errors) == 0

        if is_valid:
            logger.info("Plan validation passed", totals=totals, num_seeds=num_seeds)
        else:
            logger.warning("Plan validation failed", errors=errors, totals=totals)

        return is_valid, errors

    @staticmethod
    def _calculate_totals(allocations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate total posts, video_posts, and image_posts from allocations.

        Uses unified format counting:
        - Each image_post creates 2 posts (IG + FB)
        - Each video_post creates 2 posts (IG + FB)
        - Each text_only_post creates 1 post (FB only)
        """
        totals = {
            "posts": 0,           # Total platform posts (counting both IG + FB)
            "post_units": 0,      # Total post units (not counting duplication)
            "image_posts": 0,     # Image post units
            "video_posts": 0,     # Video post units
            "text_only_posts": 0  # Text-only post units (FB only)
        }

        for allocation in allocations:
            image_posts = allocation.get("image_posts", 0)
            video_posts = allocation.get("video_posts", 0)
            text_only_posts = allocation.get("text_only_posts", 0)

            # Count post units
            totals["image_posts"] += image_posts
            totals["video_posts"] += video_posts
            totals["text_only_posts"] += text_only_posts
            totals["post_units"] += image_posts + video_posts + text_only_posts

            # Count total platform posts (each image/video creates 2, text_only creates 1)
            totals["posts"] += (image_posts * 2) + (video_posts * 2) + text_only_posts

        return totals

    @staticmethod
    def _validate_allocation(allocation: Dict[str, Any], index: int) -> List[str]:
        """Validate a single allocation."""
        errors = []

        # Check required fields
        required_fields = [
            "seed_id",
            "seed_type",
            "image_posts",
            "video_posts",
            "text_only_posts",
            "image_budget",
            "video_budget"
        ]

        for field in required_fields:
            if field not in allocation:
                errors.append(f"Allocation {index}: Missing required field '{field}'")

        # Validate seed_type
        valid_types = ["news_event", "trend", "ungrounded"]
        seed_type = allocation.get("seed_type")
        if seed_type and seed_type not in valid_types:
            errors.append(
                f"Allocation {index}: Invalid seed_type '{seed_type}' "
                f"(must be one of: {', '.join(valid_types)})"
            )

        # Validate counts are non-negative integers
        count_fields = [
            "image_posts",
            "video_posts",
            "text_only_posts",
            "image_budget",
            "video_budget"
        ]

        for field in count_fields:
            value = allocation.get(field, 0)
            if not isinstance(value, int) or value < 0:
                errors.append(
                    f"Allocation {index}: Field '{field}' must be a non-negative integer (got: {value})"
                )

        # Validate text_only isolation: text_only_posts should only be in separate allocations
        image_posts = allocation.get("image_posts", 0)
        video_posts = allocation.get("video_posts", 0)
        text_only_posts = allocation.get("text_only_posts", 0)

        if text_only_posts > 0 and (image_posts > 0 or video_posts > 0):
            errors.append(
                f"Allocation {index}: text_only_posts cannot be mixed with image_posts or video_posts. "
                f"Use separate allocations for text-only content."
            )

        # Validate scheduled_times count matches post units (if provided)
        scheduled_times = allocation.get("scheduled_times", [])
        post_units = image_posts + video_posts + text_only_posts
        if scheduled_times and len(scheduled_times) != post_units:
            errors.append(
                f"Allocation {index}: scheduled_times count ({len(scheduled_times)}) "
                f"doesn't match post units ({post_units})"
            )

        return errors


def validate_plan(plan: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Convenience function for validating a plan.

    Args:
        plan: Planner output dictionary

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    return PlannerValidator.validate(plan)
