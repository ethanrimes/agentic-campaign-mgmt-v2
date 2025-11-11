# backend/utils/validators.py

"""
Common validation utilities for the framework.
"""

from datetime import datetime
import re


def validate_url(url: str) -> bool:
    """
    Validate that a string is a properly formatted URL.

    Args:
        url: URL string to validate

    Returns:
        True if valid, False otherwise
    """
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or IP
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return url_pattern.match(url) is not None


def validate_iso_timestamp(timestamp: str) -> bool:
    """
    Validate that a string is a valid ISO 8601 timestamp.

    Args:
        timestamp: Timestamp string to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return True
    except (ValueError, AttributeError):
        return False


def validate_platform(platform: str) -> bool:
    """
    Validate that platform is one of the supported values.

    Args:
        platform: Platform name

    Returns:
        True if valid, False otherwise
    """
    return platform.lower() in ["facebook", "instagram"]


def validate_content_seed_type(seed_type: str) -> bool:
    """
    Validate that seed type is one of the supported values.

    Args:
        seed_type: Content seed type

    Returns:
        True if valid, False otherwise
    """
    return seed_type.lower() in ["news_event", "trend", "ungrounded"]


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing/replacing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem use
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:200 - len(ext) - 1] + "." + ext if ext else name[:200]
    return filename


def validate_media_type(media_type: str) -> bool:
    """
    Validate that media type is supported.

    Args:
        media_type: Media type (e.g., 'image/png', 'video/mp4')

    Returns:
        True if valid, False otherwise
    """
    valid_types = [
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/webp",
        "video/mp4",
        "video/quicktime",
    ]
    return media_type.lower() in valid_types
