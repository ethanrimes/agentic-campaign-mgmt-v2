# backend/services/wavespeed/__init__.py

from .image_generator import ImageGenerator
from .video_generator import VideoGenerator

__all__ = ["ImageGenerator", "VideoGenerator"]
