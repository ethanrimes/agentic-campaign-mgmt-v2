# backend/agents/planner/validator.py

"""Planner output validation against guardrails."""

from typing import Dict, Any, List, Tuple
from backend.config.guardrails_config import GuardrailsConfig
from backend.utils import get_logger

logger = get_logger(__name__)


class PlannerValidator:
    """
    Validates planner output against guardrails.

    Ensures plans meet all min/max constraints before execution.
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

        # Validate total posts
        if totals["posts"] < GuardrailsConfig.min_posts_per_week:
            errors.append(
                f"Total posts ({totals['posts']}) is below minimum ({GuardrailsConfig.min_posts_per_week})"
            )
        if totals["posts"] > GuardrailsConfig.max_posts_per_week:
            errors.append(
                f"Total posts ({totals['posts']}) exceeds maximum ({GuardrailsConfig.max_posts_per_week})"
            )

        # Validate total seeds
        num_seeds = len(allocations)
        if num_seeds < GuardrailsConfig.min_content_seeds_per_week:
            errors.append(
                f"Number of content seeds ({num_seeds}) is below minimum ({GuardrailsConfig.min_content_seeds_per_week})"
            )
        if num_seeds > GuardrailsConfig.max_content_seeds_per_week:
            errors.append(
                f"Number of content seeds ({num_seeds}) exceeds maximum ({GuardrailsConfig.max_content_seeds_per_week})"
            )

        # Validate total videos
        if totals["videos"] < GuardrailsConfig.min_videos_per_week:
            errors.append(
                f"Total videos ({totals['videos']}) is below minimum ({GuardrailsConfig.min_videos_per_week})"
            )
        if totals["videos"] > GuardrailsConfig.max_videos_per_week:
            errors.append(
                f"Total videos ({totals['videos']}) exceeds maximum ({GuardrailsConfig.max_videos_per_week})"
            )

        # Validate total images
        if totals["images"] < GuardrailsConfig.min_images_per_week:
            errors.append(
                f"Total images ({totals['images']}) is below minimum ({GuardrailsConfig.min_images_per_week})"
            )
        if totals["images"] > GuardrailsConfig.max_images_per_week:
            errors.append(
                f"Total images ({totals['images']}) exceeds maximum ({GuardrailsConfig.max_images_per_week})"
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
        """Calculate total posts, videos, and images from allocations."""
        totals = {
            "posts": 0,
            "videos": 0,
            "images": 0
        }

        for allocation in allocations:
            # Count posts
            instagram_image = allocation.get("instagram_image_posts", 0)
            instagram_reel = allocation.get("instagram_reel_posts", 0)
            facebook_feed = allocation.get("facebook_feed_posts", 0)
            facebook_video = allocation.get("facebook_video_posts", 0)

            totals["posts"] += instagram_image + instagram_reel + facebook_feed + facebook_video

            # Count videos (reels and video posts are videos)
            totals["videos"] += instagram_reel + facebook_video

            # Count images (from budgets)
            totals["images"] += allocation.get("image_budget", 0)

        return totals

    @staticmethod
    def _validate_allocation(allocation: Dict[str, Any], index: int) -> List[str]:
        """Validate a single allocation."""
        errors = []

        # Check required fields
        required_fields = [
            "seed_id",
            "seed_type",
            "instagram_image_posts",
            "instagram_reel_posts",
            "facebook_feed_posts",
            "facebook_video_posts",
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

        # Validate counts are non-negative
        count_fields = [
            "instagram_image_posts",
            "instagram_reel_posts",
            "facebook_feed_posts",
            "facebook_video_posts",
            "image_budget",
            "video_budget"
        ]

        for field in count_fields:
            value = allocation.get(field, 0)
            if not isinstance(value, int) or value < 0:
                errors.append(
                    f"Allocation {index}: Field '{field}' must be a non-negative integer (got: {value})"
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
