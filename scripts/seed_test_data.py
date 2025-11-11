# scripts/seed_test_data.py

"""
Seed test data for development.

Usage:
    python scripts/seed_test_data.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from datetime import datetime
from backend.models import NewsEventSeed, TrendSeed, UngroundedSeed
from backend.database.repositories import (
    NewsEventSeedRepository,
    TrendSeedRepository,
    UngroundedSeedRepository,
)

print("🌱 Seeding test data...\n")

# News Event Seeds
news_repo = NewsEventSeedRepository()

news_seed = NewsEventSeed(
    name="SEPTA Fare Increase",
    start_time="2025-01-15T00:00:00Z",
    end_time=None,
    location="Philadelphia, PA",
    description="SEPTA announced a 15% fare increase effective March 2025. This is the first increase in five years, driven by rising costs and declining ridership.",
    sources=[],
)

try:
    news_repo.create(news_seed)
    print("  ✅ Created news event seed: SEPTA Fare Increase")
except Exception as e:
    print(f"  ⚠️  News seed may already exist: {e}")

# Trend Seeds
trend_repo = TrendSeedRepository()

trend_seed = TrendSeed(
    name="Penn Campus Winter Aesthetic",
    description="Students sharing photos of snowy campus, emphasizing Dark Academia aesthetic popular with Gen Z.",
    hashtags=["PennWinter", "DarkAcademia", "UPenn", "CampusBeauty"],
    posts=[],
    users=[],
    created_by="gpt-4o-mini",
)

try:
    trend_repo.create(trend_seed)
    print("  ✅ Created trend seed: Penn Campus Winter Aesthetic")
except Exception as e:
    print(f"  ⚠️  Trend seed may already exist: {e}")

# Ungrounded Seeds
ungrounded_repo = UngroundedSeedRepository()

ungrounded_seed = UngroundedSeed(
    idea="Study spot recommendations from current students",
    format="carousel",
    details="Multi-image carousel showcasing 5 underrated study spots on campus. Each image shows location with student testimonial.",
    created_by="gpt-4o-mini",
)

try:
    ungrounded_repo.create(ungrounded_seed)
    print("  ✅ Created ungrounded seed: Study spot recommendations")
except Exception as e:
    print(f"  ⚠️  Ungrounded seed may already exist: {e}")

print("\n✅ Test data seeded!")
