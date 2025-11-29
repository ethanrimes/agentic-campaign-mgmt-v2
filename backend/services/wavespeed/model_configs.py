# backend/services/wavespeed/model_configs.py

"""
Model configurations for Wavespeed AI.
Each model defines its endpoint, supported parameters, and payload builder.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Literal


@dataclass
class ModelConfig(ABC):
    """Base configuration for a Wavespeed model."""

    model_id: str  # Full model path used as API endpoint

    @abstractmethod
    def build_payload(self, **kwargs) -> Dict[str, Any]:
        """Build the API payload for this model."""
        pass

    @property
    @abstractmethod
    def media_type(self) -> Literal["image", "video"]:
        """Return the type of media this model generates."""
        pass


# =============================================================================
# IMAGE MODELS
# =============================================================================

@dataclass
class SDXLLoraConfig(ModelConfig):
    """Configuration for stability-ai/sdxl-lora model."""

    model_id: str = "stability-ai/sdxl-lora"

    @property
    def media_type(self) -> Literal["image", "video"]:
        return "image"

    def build_payload(
        self,
        prompt: str,
        size: str = "1024*1024",
        negative_prompt: str = "",
        guidance_scale: float = 3.5,
        num_inference_steps: int = 28,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Build payload for SDXL-LoRA.

        Args:
            prompt: Text prompt for generation
            size: Image size in format "width*height" (range: 1024-4096 each)
            negative_prompt: Negative prompt text
            guidance_scale: CFG scale (1-20, default 3.5)
            num_inference_steps: Denoising steps (1-50, default 28)
        """
        return {
            "prompt": prompt,
            "size": size,
            "negative_prompt": negative_prompt,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps,
            "seed": -1,  # Fixed
            "enable_base64_output": False,  # Fixed
            "loras": [],
        }


@dataclass
class SeedreamV4Config(ModelConfig):
    """Configuration for bytedance/seedream-v4 model."""

    model_id: str = "bytedance/seedream-v4"

    @property
    def media_type(self) -> Literal["image", "video"]:
        return "image"

    def build_payload(
        self,
        prompt: str,
        size: str = "1024*1024",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Build payload for Seedream V4.

        Args:
            prompt: Text prompt for generation
            size: Image size in format "width*height" (range: 1024-4096 each)
        """
        return {
            "prompt": prompt,
            "size": size,
            "enable_base64_output": False,  # Fixed
            "enable_sync_mode": False,  # Async mode to match current setup
        }


# =============================================================================
# VIDEO MODELS
# =============================================================================

@dataclass
class WAN22I2VConfig(ModelConfig):
    """Configuration for wavespeed-ai/wan-2.2/i2v-5b-720p model."""

    model_id: str = "wavespeed-ai/wan-2.2/i2v-5b-720p"

    @property
    def media_type(self) -> Literal["image", "video"]:
        return "video"

    def build_payload(
        self,
        prompt: str,
        size: str = "1280*720",
        seed: int = -1,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Build payload for WAN 2.2 I2V.

        Args:
            prompt: Text prompt for generation
            size: Video size - "1280*720" or "720*1280"
            seed: Random seed (default -1 for random)
        """
        # Validate size
        valid_sizes = ["1280*720", "720*1280"]
        if size not in valid_sizes:
            size = "1280*720"  # Default to landscape

        return {
            "prompt": prompt,
            "size": size,
            "seed": seed,
        }


@dataclass
class SeedanceV1ProT2VConfig(ModelConfig):
    """Configuration for bytedance/seedance-v1-pro-t2v-480p model."""

    model_id: str = "bytedance/seedance-v1-pro-t2v-480p"

    @property
    def media_type(self) -> Literal["image", "video"]:
        return "video"

    def build_payload(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        camera_fixed: bool = False,
        seed: int = -1,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Build payload for Seedance V1 Pro T2V.

        Args:
            prompt: Text prompt for generation
            aspect_ratio: One of "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"
            camera_fixed: Whether to fix the camera position
            seed: Random seed (default -1 for random)
        """
        # Validate aspect ratio
        valid_ratios = ["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"]
        if aspect_ratio not in valid_ratios:
            aspect_ratio = "16:9"  # Default

        return {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "duration": 5,  # Fixed at 5 seconds
            "camera_fixed": camera_fixed,
            "seed": seed,
        }


# =============================================================================
# MODEL REGISTRY
# =============================================================================

# Map model IDs to their config classes
IMAGE_MODEL_CONFIGS: Dict[str, type[ModelConfig]] = {
    "stability-ai/sdxl-lora": SDXLLoraConfig,
    "bytedance/seedream-v4": SeedreamV4Config,
}

VIDEO_MODEL_CONFIGS: Dict[str, type[ModelConfig]] = {
    "wavespeed-ai/wan-2.2/i2v-5b-720p": WAN22I2VConfig,
    "bytedance/seedance-v1-pro-t2v-480p": SeedanceV1ProT2VConfig,
}

ALL_MODEL_CONFIGS: Dict[str, type[ModelConfig]] = {
    **IMAGE_MODEL_CONFIGS,
    **VIDEO_MODEL_CONFIGS,
}


def get_model_config(model_id: str) -> ModelConfig:
    """
    Get the configuration instance for a model.

    Args:
        model_id: The model identifier (e.g., "stability-ai/sdxl-lora")

    Returns:
        Instantiated ModelConfig for the model

    Raises:
        ValueError: If the model is not supported
    """
    if model_id not in ALL_MODEL_CONFIGS:
        supported = list(ALL_MODEL_CONFIGS.keys())
        raise ValueError(
            f"Unsupported model: {model_id}. Supported models: {supported}"
        )

    config_class = ALL_MODEL_CONFIGS[model_id]
    return config_class()


def get_image_model_config(model_id: str) -> ModelConfig:
    """Get configuration for an image model."""
    if model_id not in IMAGE_MODEL_CONFIGS:
        supported = list(IMAGE_MODEL_CONFIGS.keys())
        raise ValueError(
            f"Unsupported image model: {model_id}. Supported: {supported}"
        )
    return IMAGE_MODEL_CONFIGS[model_id]()


def get_video_model_config(model_id: str) -> ModelConfig:
    """Get configuration for a video model."""
    if model_id not in VIDEO_MODEL_CONFIGS:
        supported = list(VIDEO_MODEL_CONFIGS.keys())
        raise ValueError(
            f"Unsupported video model: {model_id}. Supported: {supported}"
        )
    return VIDEO_MODEL_CONFIGS[model_id]()
