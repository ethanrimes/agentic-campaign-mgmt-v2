# backend/services/wavespeed/__init__.py

from .image_generator import ImageGenerator
from .video_generator import VideoGenerator
from .model_configs import (
    ModelConfig,
    SDXLLoraConfig,
    SeedreamV4Config,
    WAN22I2VConfig,
    SeedanceV1ProT2VConfig,
    IMAGE_MODEL_CONFIGS,
    VIDEO_MODEL_CONFIGS,
    ALL_MODEL_CONFIGS,
    get_model_config,
    get_image_model_config,
    get_video_model_config,
)

__all__ = [
    # Generators
    "ImageGenerator",
    "VideoGenerator",
    # Model configs
    "ModelConfig",
    "SDXLLoraConfig",
    "SeedreamV4Config",
    "WAN22I2VConfig",
    "SeedanceV1ProT2VConfig",
    # Registries
    "IMAGE_MODEL_CONFIGS",
    "VIDEO_MODEL_CONFIGS",
    "ALL_MODEL_CONFIGS",
    # Helper functions
    "get_model_config",
    "get_image_model_config",
    "get_video_model_config",
]
