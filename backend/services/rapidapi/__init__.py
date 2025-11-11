# backend/services/rapidapi/__init__.py

from .instagram_scraper import InstagramScraper
from .facebook_scraper import FacebookScraper

__all__ = ["InstagramScraper", "FacebookScraper"]
