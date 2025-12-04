# backend/database/repositories/__init__.py

from .base import BaseRepository
from .news_event_seeds import NewsEventSeedRepository, IngestedEventRepository
from .trend_seeds import TrendSeedsRepository
from .ungrounded_seeds import UngroundedSeedRepository
from .insights import InsightsRepository
from .insights_metrics import (
    FacebookPageInsightsRepository,
    FacebookPostInsightsRepository,
    FacebookVideoInsightsRepository,
    InstagramAccountInsightsRepository,
    InstagramMediaInsightsRepository,
)
from .content_creation_tasks import ContentCreationTaskRepository
from .completed_posts import CompletedPostRepository
from .media import MediaRepository
from .sources import SourceRepository
from .platform_comments import PlatformCommentRepository
from .verifier_responses import VerifierResponseRepository

__all__ = [
    "BaseRepository",
    "NewsEventSeedRepository",
    "IngestedEventRepository",
    "TrendSeedsRepository",
    "UngroundedSeedRepository",
    "InsightsRepository",
    # Cached insights metrics repositories
    "FacebookPageInsightsRepository",
    "FacebookPostInsightsRepository",
    "FacebookVideoInsightsRepository",
    "InstagramAccountInsightsRepository",
    "InstagramMediaInsightsRepository",
    # Other repositories
    "ContentCreationTaskRepository",
    "CompletedPostRepository",
    "MediaRepository",
    "SourceRepository",
    "PlatformCommentRepository",
    "VerifierResponseRepository",
]
