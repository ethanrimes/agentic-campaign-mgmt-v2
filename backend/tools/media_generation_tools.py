# backend/tools/media_generation_tools.py

"""Langchain tools for AI media generation via Wavespeed."""

from typing import Type, Literal
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from backend.services.wavespeed.image_generator import ImageGenerator
from backend.services.wavespeed.video_generator import VideoGenerator
from backend.services.supabase.storage import StorageService
from backend.database.repositories.media import MediaRepository
from backend.models.media import Image, Video
from backend.utils import get_logger

logger = get_logger(__name__)


class GenerateImageInput(BaseModel):
    """Input for GenerateImage tool."""
    prompt: str = Field(..., description="Text prompt describing the image to generate")
    size: str = Field(
        None,
        description="Image size. Options: 'square' (2048*2048), 'portrait' (1920*2400), 'landscape' (2400*1920). Defaults to square."
    )
    guidance_scale: float = Field(7.5, description="Guidance scale (1-20, default: 7.5)")


class GenerateImageTool(BaseTool):
    """Tool to generate images using Wavespeed AI."""

    name: str = "generate_image"
    description: str = """
    Generate an AI image from a text prompt using Wavespeed SDXL-LoRA.
    The generated image will be automatically uploaded to storage.
    Returns the public URL of the generated image.
    Use this to create visual content for social media posts.
    """
    args_schema: Type[BaseModel] = GenerateImageInput
    business_asset_id: str = ""  # Will be set during initialization

    def _run(
        self,
        prompt: str,
        size: str = None,
        guidance_scale: float = 7.5
    ) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(
        self,
        prompt: str,
        size: str = None,
        guidance_scale: float = 7.5
    ) -> str:
        """Execute the tool asynchronously."""
        try:
            from datetime import datetime, timezone
            from uuid import uuid4
            from backend.services.wavespeed.model_configs import ImageSize

            generator = ImageGenerator()
            storage = StorageService()
            media_repo = MediaRepository()

            # Map friendly names to ImageSize enum
            size_mapping = {
                "square": ImageSize.SQUARE,
                "portrait": ImageSize.PORTRAIT_4_5,
                "landscape": ImageSize.LANDSCAPE_FACEBOOK,
            }
            actual_size = size_mapping.get(size, size) if size else None

            # Generate image (returns bytes directly)
            logger.info("Generating image", prompt=prompt, size=actual_size)
            image_bytes = await generator.generate(prompt, actual_size, guidance_scale=guidance_scale)

            # Generate unique filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            file_id = uuid4().hex[:8]
            filename = f"{timestamp}_{file_id}.png"

            # Upload to Supabase
            storage_path = f"ai-generated/images/{filename}"
            public_url = await storage.upload_media(
                storage_path,
                image_bytes,
                "image/png"
            )

            # Create Image model
            image = Image(
                business_asset_id=self.business_asset_id,
                storage_path=storage_path,
                public_url=public_url,
                prompt=prompt,
                file_size=len(image_bytes),
                mime_type="image/png"
            )

            # Save to database
            saved_image = await media_repo.create_image(image)

            logger.info("Image generated successfully", url=public_url, media_id=str(saved_image.id))
            return f"Image generated successfully!\nURL: {public_url}\nMedia ID: {saved_image.id}\nPrompt: {prompt}"

        except Exception as e:
            logger.error("Error generating image", error=str(e))
            return f"Error generating image: {str(e)}"


class GenerateVideoInput(BaseModel):
    """Input for GenerateVideo tool."""
    prompt: str = Field(..., description="Text prompt describing the desired video content and motion")
    orientation: Literal["landscape", "portrait"] = Field(
        "landscape",
        description="Video orientation: 'landscape' (1280x720) or 'portrait' (720x1280)"
    )
    seed: int = Field(-1, description="Random seed (-1 for random, or specific number for reproducibility)")


class GenerateVideoTool(BaseTool):
    """Tool to generate videos using Wavespeed AI."""

    name: str = "generate_video"
    description: str = """
    Generate an AI video from a text prompt using Wavespeed WAN-2.2 (text-to-video).
    Creates dynamic video content based on the text description.
    Returns the public URL of the generated video.
    Use this to create video content for social media posts.
    Choose 'landscape' for horizontal videos or 'portrait' for vertical/story videos.
    Note: Video generation takes 1-5 minutes depending on complexity.
    """
    args_schema: Type[BaseModel] = GenerateVideoInput
    business_asset_id: str = ""  # Will be set during initialization

    def _run(
        self,
        prompt: str,
        orientation: str = "landscape",
        seed: int = -1
    ) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(
        self,
        prompt: str,
        orientation: str = "landscape",
        seed: int = -1
    ) -> str:
        """Execute the tool asynchronously."""
        try:
            from datetime import datetime, timezone
            from uuid import uuid4

            # Map orientation to actual size
            size_map = {
                "landscape": "1280*720",
                "portrait": "720*1280"
            }
            size = size_map.get(orientation, "1280*720")

            generator = VideoGenerator()
            storage = StorageService()
            media_repo = MediaRepository()

            # Generate video (returns bytes directly)
            logger.info("Generating video", prompt=prompt, orientation=orientation, size=size)
            video_bytes = await generator.generate(prompt, size, seed)

            # Generate unique filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            file_id = uuid4().hex[:8]
            filename = f"{timestamp}_{file_id}.mp4"

            # Upload to Supabase
            storage_path = f"ai-generated/videos/{filename}"
            public_url = await storage.upload_media(
                storage_path,
                video_bytes,
                "video/mp4"
            )

            # Create Video model
            video = Video(
                business_asset_id=self.business_asset_id,
                storage_path=storage_path,
                public_url=public_url,
                prompt=prompt,
                file_size=len(video_bytes),
                mime_type="video/mp4"
            )

            # Save to database
            saved_video = await media_repo.create_video(video)

            logger.info("Video generated successfully", url=public_url, media_id=str(saved_video.id))
            return f"Video generated successfully!\nURL: {public_url}\nMedia ID: {saved_video.id}\nPrompt: {prompt}"

        except Exception as e:
            logger.error("Error generating video", error=str(e))
            return f"Error generating video: {str(e)}"


class GenerateImageAndVideoInput(BaseModel):
    """Input for GenerateImageAndVideo tool."""
    image_prompt: str = Field(..., description="Text prompt for generating the image")
    video_prompt: str = Field(..., description="Text prompt for generating the video")
    image_size: str = Field(
        None,
        description="Image size. Options: 'square' (2048*2048), 'portrait' (1920*2400), 'landscape' (2400*1920). Defaults to square."
    )
    video_orientation: Literal["landscape", "portrait"] = Field(
        "landscape",
        description="Video orientation: 'landscape' (1280x720) or 'portrait' (720x1280)"
    )


class GenerateImageAndVideoTool(BaseTool):
    """Tool to generate both an image and video in one step."""

    name: str = "generate_image_and_video"
    description: str = """
    Generate both an AI image and video in one workflow.
    Generates an image from image_prompt and a video from video_prompt independently.
    Returns both the image URL and video URL.
    Use this when you need both image and video content for a post.
    Choose 'landscape' for horizontal videos or 'portrait' for vertical/story videos.
    Note: This takes 1-5 minutes due to video generation time.
    """
    args_schema: Type[BaseModel] = GenerateImageAndVideoInput
    business_asset_id: str = ""  # Will be set during initialization

    def _run(
        self,
        image_prompt: str,
        video_prompt: str,
        image_size: str = None,
        video_orientation: str = "landscape"
    ) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(
        self,
        image_prompt: str,
        video_prompt: str,
        image_size: str = None,
        video_orientation: str = "landscape"
    ) -> str:
        """Execute the tool asynchronously."""
        try:
            from datetime import datetime, timezone
            from uuid import uuid4
            from backend.services.wavespeed.model_configs import ImageSize

            # Map orientation to actual size for video
            size_map = {
                "landscape": "1280*720",
                "portrait": "720*1280"
            }
            video_size = size_map.get(video_orientation, "1280*720")

            # Map friendly names to ImageSize enum for image
            image_size_mapping = {
                "square": ImageSize.SQUARE,
                "portrait": ImageSize.PORTRAIT_4_5,
                "landscape": ImageSize.LANDSCAPE_FACEBOOK,
            }
            actual_image_size = image_size_mapping.get(image_size, image_size) if image_size else None

            image_gen = ImageGenerator()
            video_gen = VideoGenerator()
            storage = StorageService()
            media_repo = MediaRepository()

            # Step 1: Generate image (returns bytes directly)
            logger.info("Generating image", prompt=image_prompt, size=actual_image_size)
            image_bytes = await image_gen.generate(image_prompt, actual_image_size)

            # Generate unique filename for image
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            file_id = uuid4().hex[:8]
            image_filename = f"{timestamp}_{file_id}.png"

            # Upload image to Supabase
            image_path = f"ai-generated/images/{image_filename}"
            image_url = await storage.upload_media(image_path, image_bytes, "image/png")

            # Create Image model and save to database
            image_model = Image(
                business_asset_id=self.business_asset_id,
                storage_path=image_path,
                public_url=image_url,
                prompt=image_prompt,
                file_size=len(image_bytes),
                mime_type="image/png"
            )
            saved_image = await media_repo.create_image(image_model)

            # Step 2: Generate video independently (text-to-video)
            logger.info("Generating video", prompt=video_prompt, orientation=video_orientation, size=video_size)
            video_bytes = await video_gen.generate(video_prompt, video_size)

            # Generate unique filename for video
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            file_id = uuid4().hex[:8]
            video_filename = f"{timestamp}_{file_id}.mp4"

            # Upload video to Supabase
            video_path = f"ai-generated/videos/{video_filename}"
            video_url = await storage.upload_media(video_path, video_bytes, "video/mp4")

            # Create Video model and save to database
            video_model = Video(
                business_asset_id=self.business_asset_id,
                storage_path=video_path,
                public_url=video_url,
                prompt=video_prompt,
                file_size=len(video_bytes),
                mime_type="video/mp4"
            )
            saved_video = await media_repo.create_video(video_model)

            logger.info("Image and video generated successfully")
            return f"""Image and Video generated successfully!

Image:
  URL: {image_url}
  Media ID: {saved_image.id}
  Prompt: {image_prompt}

Video:
  URL: {video_url}
  Media ID: {saved_video.id}
  Prompt: {video_prompt}
"""

        except Exception as e:
            logger.error("Error generating image and video", error=str(e))
            return f"Error generating image and video: {str(e)}"


def create_media_generation_tools(business_asset_id: str):
    """Create all media generation tools for use with Langchain agents."""
    return [
        GenerateImageTool(business_asset_id=business_asset_id),
        GenerateVideoTool(business_asset_id=business_asset_id),
        GenerateImageAndVideoTool(business_asset_id=business_asset_id),
    ]
