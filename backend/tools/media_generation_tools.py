# backend/tools/media_generation_tools.py

"""Langchain tools for AI media generation via Wavespeed."""

from typing import Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from backend.services.wavespeed.image_generator import ImageGenerator
from backend.services.wavespeed.video_generator import VideoGenerator
from backend.services.supabase.storage import StorageService
from backend.database.repositories.media import MediaRepository
from backend.utils import get_logger

logger = get_logger(__name__)


class GenerateImageInput(BaseModel):
    """Input for GenerateImage tool."""
    prompt: str = Field(..., description="Text prompt describing the image to generate")
    size: str = Field("1024*1024", description="Image size (e.g., '1024*1024', '1024*768')")
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

    def _run(
        self,
        prompt: str,
        size: str = "1024*1024",
        guidance_scale: float = 7.5
    ) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(
        self,
        prompt: str,
        size: str = "1024*1024",
        guidance_scale: float = 7.5
    ) -> str:
        """Execute the tool asynchronously."""
        try:
            generator = ImageGenerator()
            storage = StorageService()
            media_repo = MediaRepository()

            # Generate image
            logger.info("Generating image", prompt=prompt)
            temp_url = await generator.generate(prompt, size, guidance_scale)

            # Download from Wavespeed
            image_bytes = await generator.download_media(temp_url)

            # Upload to Supabase
            storage_path = f"ai-generated/images/{generator._generate_filename()}.png"
            public_url = await storage.upload_media(
                storage_path,
                image_bytes,
                "image/png"
            )

            # Save to database
            media_id = await media_repo.create({
                "type": "image",
                "url": public_url,
                "storage_path": storage_path,
                "generation_prompt": prompt,
                "file_size": len(image_bytes)
            })

            logger.info("Image generated successfully", url=public_url, media_id=media_id)
            return f"Image generated successfully!\nURL: {public_url}\nMedia ID: {media_id}\nPrompt: {prompt}"

        except Exception as e:
            logger.error("Error generating image", error=str(e))
            return f"Error generating image: {str(e)}"


class GenerateVideoInput(BaseModel):
    """Input for GenerateVideo tool."""
    image_url: str = Field(..., description="URL of the input image to animate")
    prompt: str = Field(..., description="Text prompt describing the desired video motion/animation")
    seed: int = Field(-1, description="Random seed (-1 for random, or specific number for reproducibility)")


class GenerateVideoTool(BaseTool):
    """Tool to generate videos using Wavespeed AI."""

    name: str = "generate_video"
    description: str = """
    Generate an AI video from an input image using Wavespeed WAN-2.2.
    The input image will be animated according to the prompt.
    Returns the public URL of the generated video.
    Use this to create dynamic video content from static images.
    """
    args_schema: Type[BaseModel] = GenerateVideoInput

    def _run(
        self,
        image_url: str,
        prompt: str,
        seed: int = -1
    ) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(
        self,
        image_url: str,
        prompt: str,
        seed: int = -1
    ) -> str:
        """Execute the tool asynchronously."""
        try:
            generator = VideoGenerator()
            storage = StorageService()
            media_repo = MediaRepository()

            # Generate video
            logger.info("Generating video", prompt=prompt, image_url=image_url)
            temp_url = await generator.generate(image_url, prompt, seed)

            # Download from Wavespeed
            video_bytes = await generator.download_media(temp_url)

            # Upload to Supabase
            storage_path = f"ai-generated/videos/{generator._generate_filename()}.mp4"
            public_url = await storage.upload_media(
                storage_path,
                video_bytes,
                "video/mp4"
            )

            # Save to database
            media_id = await media_repo.create({
                "type": "video",
                "url": public_url,
                "storage_path": storage_path,
                "generation_prompt": prompt,
                "source_image": image_url,
                "file_size": len(video_bytes)
            })

            logger.info("Video generated successfully", url=public_url, media_id=media_id)
            return f"Video generated successfully!\nURL: {public_url}\nMedia ID: {media_id}\nPrompt: {prompt}"

        except Exception as e:
            logger.error("Error generating video", error=str(e))
            return f"Error generating video: {str(e)}"


class GenerateImageAndVideoInput(BaseModel):
    """Input for GenerateImageAndVideo tool."""
    image_prompt: str = Field(..., description="Text prompt for generating the base image")
    video_prompt: str = Field(..., description="Text prompt for animating the image into video")
    image_size: str = Field("1024*1024", description="Image size (default: '1024*1024')")


class GenerateImageAndVideoTool(BaseTool):
    """Tool to generate both an image and video in one step."""

    name: str = "generate_image_and_video"
    description: str = """
    Generate both an AI image and video in one workflow.
    First generates an image from image_prompt, then animates it with video_prompt.
    Returns both the image URL and video URL.
    Use this when you need both image and video content from the same concept.
    """
    args_schema: Type[BaseModel] = GenerateImageAndVideoInput

    def _run(
        self,
        image_prompt: str,
        video_prompt: str,
        image_size: str = "1024*1024"
    ) -> str:
        """Sync version - not used by async agents."""
        raise NotImplementedError("Use async version (_arun) instead")

    async def _arun(
        self,
        image_prompt: str,
        video_prompt: str,
        image_size: str = "1024*1024"
    ) -> str:
        """Execute the tool asynchronously."""
        try:
            image_gen = ImageGenerator()
            video_gen = VideoGenerator()
            storage = StorageService()
            media_repo = MediaRepository()

            # Step 1: Generate image
            logger.info("Generating image", prompt=image_prompt)
            temp_image_url = await image_gen.generate(image_prompt, image_size)
            image_bytes = await image_gen.download_media(temp_image_url)

            # Upload image to Supabase
            image_path = f"ai-generated/images/{image_gen._generate_filename()}.png"
            image_url = await storage.upload_media(image_path, image_bytes, "image/png")

            # Save image to database
            image_id = await media_repo.create({
                "type": "image",
                "url": image_url,
                "storage_path": image_path,
                "generation_prompt": image_prompt,
                "file_size": len(image_bytes)
            })

            # Step 2: Generate video from the image
            logger.info("Generating video from image", prompt=video_prompt)
            temp_video_url = await video_gen.generate(image_url, video_prompt)
            video_bytes = await video_gen.download_media(temp_video_url)

            # Upload video to Supabase
            video_path = f"ai-generated/videos/{video_gen._generate_filename()}.mp4"
            video_url = await storage.upload_media(video_path, video_bytes, "video/mp4")

            # Save video to database
            video_id = await media_repo.create({
                "type": "video",
                "url": video_url,
                "storage_path": video_path,
                "generation_prompt": video_prompt,
                "source_image": image_url,
                "file_size": len(video_bytes)
            })

            logger.info("Image and video generated successfully")
            return f"""Image and Video generated successfully!

Image:
  URL: {image_url}
  Media ID: {image_id}
  Prompt: {image_prompt}

Video:
  URL: {video_url}
  Media ID: {video_id}
  Prompt: {video_prompt}
"""

        except Exception as e:
            logger.error("Error generating image and video", error=str(e))
            return f"Error generating image and video: {str(e)}"


def create_media_generation_tools():
    """Create all media generation tools for use with Langchain agents."""
    return [
        GenerateImageTool(),
        GenerateVideoTool(),
        GenerateImageAndVideoTool(),
    ]
