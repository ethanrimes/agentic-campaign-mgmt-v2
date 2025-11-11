# backend/services/wavespeed/__init__.py

from .image_generator import WavespeedImageGenerator
from .video_generator import WavespeedVideoGenerator

__all__ = ["WavespeedImageGenerator", "WavespeedVideoGenerator"]
