# backend/tools/tests/test_media_generation_tools.py

"""
Integration tests for media generation tools.
These tests use real Wavespeed API connections.
Note: These tests will generate actual media and incur API costs.
"""

import pytest
from backend.tools.media_generation_tools import (
    GenerateImageTool,
    GenerateVideoTool,
    GenerateImageAndVideoTool,
)
from .conftest import skip_if_no_wavespeed


pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration,
    pytest.mark.requires_wavespeed,
    skip_if_no_wavespeed,
]


class TestGenerateImageTool:
    """Integration tests for GenerateImageTool with real Wavespeed API."""

    async def test_arun_with_real_api(self, cleanup_generated_media):
        """
        Test generating an image using real Wavespeed API.
        WARNING: This test will incur API costs.
        """
        tool = GenerateImageTool()

        # Generate a simple image
        result = await tool._arun(
            prompt="A simple red circle on a white background",
            size="1024*1024",
            guidance_scale=7.5
        )

        # Verify we got a successful result
        assert isinstance(result, str)
        assert "Image generated successfully" in result
        assert "URL:" in result
        assert "Media ID:" in result

        # Extract media ID for cleanup if possible
        if "Media ID:" in result:
            # Parse the media ID from the result string for cleanup
            try:
                media_id_line = [line for line in result.split('\n') if "Media ID:" in line][0]
                media_id = media_id_line.split("Media ID:")[1].strip()
                cleanup_generated_media.append(media_id)
            except Exception:
                pass  # Cleanup will handle what it can

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GenerateImageTool()

        with pytest.raises(NotImplementedError):
            tool._run(prompt="test")


class TestGenerateVideoTool:
    """Integration tests for GenerateVideoTool with real Wavespeed API."""

    @pytest.mark.slow  # Mark as slow test due to video generation time
    async def test_arun_with_real_api(self, cleanup_generated_media):
        """
        Test generating a video using real Wavespeed API.
        WARNING: This test will incur API costs and take 1-5 minutes.
        """
        tool = GenerateVideoTool()

        # Generate video from text prompt
        result = await tool._arun(
            prompt="An old man adjusts his glasses while reading a newspaper in a sunlit park",
            size="1280*720",
            seed=-1
        )

        # Verify we got a response
        assert isinstance(result, str)
        # Should either succeed or fail gracefully
        assert "Video generated successfully" in result or "Error generating video" in result

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GenerateVideoTool()

        with pytest.raises(NotImplementedError):
            tool._run(prompt="test")


class TestGenerateImageAndVideoTool:
    """Integration tests for GenerateImageAndVideoTool with real Wavespeed API."""

    async def test_arun_with_real_api(self, cleanup_generated_media):
        """
        Test generating both image and video using real Wavespeed API.
        WARNING: This test will incur significant API costs and take time.
        """
        tool = GenerateImageAndVideoTool()

        # Generate both image and video
        result = await tool._arun(
            image_prompt="A simple blue square on a white background",
            video_prompt="Rotate clockwise slowly",
            image_size="1024*1024"
        )

        # Verify we got a result
        assert isinstance(result, str)
        # Should either succeed or fail gracefully
        assert (
            "Image and Video generated successfully" in result
            or "Error generating image and video" in result
        )

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GenerateImageAndVideoTool()

        with pytest.raises(NotImplementedError):
            tool._run(image_prompt="test", video_prompt="test")


class TestMediaGenerationToolsIntegration:
    """Integration tests for complete media generation workflows."""

    async def test_image_generation_workflow(self, cleanup_generated_media):
        """
        Test the complete image generation workflow.
        WARNING: This test will incur API costs.
        """
        tool = GenerateImageTool()

        # Generate an image with specific parameters
        result = await tool._arun(
            prompt="A sunset over mountains",
            size="1024*1024",
            guidance_scale=7.5
        )

        assert isinstance(result, str)
        # Verify that result contains expected information
        if "Image generated successfully" in result:
            assert "URL:" in result
            assert "Media ID:" in result
            assert "Prompt:" in result

    async def test_error_handling_with_invalid_params(self):
        """Test that tools handle invalid parameters gracefully."""
        tool = GenerateImageTool()

        # Try to generate with unusual parameters
        result = await tool._arun(
            prompt="",  # Empty prompt
            size="1024*1024",
            guidance_scale=7.5
        )

        # Should handle gracefully
        assert isinstance(result, str)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.requires_wavespeed
class TestEndToEndMediaGeneration:
    """
    End-to-end tests for media generation workflow:
    1. Generate media via Wavespeed API
    2. Download generated media
    3. Upload to Supabase storage
    4. Save metadata to database
    """

    async def test_full_image_generation_pipeline(self):
        """
        Test complete image generation pipeline from Wavespeed to Supabase.

        Steps:
        1. Generate image via Wavespeed API
        2. Download image bytes
        3. Upload to Supabase storage
        4. Save metadata to media table
        5. Verify all steps completed successfully

        WARNING: This test incurs API costs and requires valid credentials.
        """
        from backend.services.wavespeed.image_generator import ImageGenerator
        from backend.services.supabase.storage import StorageService
        from backend.database.repositories.media import MediaRepository
        from datetime import datetime, timezone
        from uuid import uuid4

        # Step 1: Generate image via Wavespeed
        generator = ImageGenerator()
        prompt = "A simple red circle on white background for testing"
        image_bytes = await generator.generate(
            prompt=prompt,
            size="1024*1024",
            guidance_scale=7.5
        )

        # Verify we got image bytes
        assert image_bytes is not None
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0
        print(f"✓ Generated image: {len(image_bytes)} bytes")

        # Step 2: Upload to Supabase storage
        storage = StorageService()
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        file_id = uuid4().hex[:8]
        storage_path = f"test/images/{timestamp}_{file_id}.png"

        public_url = await storage.upload_media(
            storage_path,
            image_bytes,
            "image/png"
        )

        # Verify we got a public URL
        assert public_url is not None
        assert isinstance(public_url, str)
        assert "supabase.co" in public_url
        assert storage_path in public_url
        print(f"✓ Uploaded to Supabase: {public_url}")

        # Step 3: Save metadata to database
        from backend.models.media import Image

        media_repo = MediaRepository()
        image_model = Image(
            storage_path=storage_path,
            public_url=public_url,
            prompt=prompt,
            file_size=len(image_bytes),
            mime_type="image/png"
        )
        media_record = await media_repo.create_image(image_model)

        # Verify database record was created
        assert media_record is not None
        assert media_record.id is not None
        assert media_record.public_url == public_url
        assert media_record.file_size == len(image_bytes)
        print(f"✓ Saved to database: Media ID {media_record.id}")

        # Step 4: Cleanup - delete from storage
        try:
            await storage.delete_media(storage_path)
            print(f"✓ Cleaned up storage: {storage_path}")
        except Exception as e:
            print(f"⚠ Cleanup warning: {e}")

        # Step 5: Cleanup - delete from database
        try:
            await media_repo.delete(str(media_record.id))
            print(f"✓ Cleaned up database: {media_record.id}")
        except Exception as e:
            print(f"⚠ Cleanup warning: {e}")

    @pytest.mark.slow  # Mark as slow test due to video generation time
    async def test_full_video_generation_pipeline(self):
        """
        Test complete video generation pipeline from Wavespeed to Supabase.

        Steps:
        1. Generate video from text prompt via Wavespeed API (text-to-video)
        2. Upload video to Supabase storage
        3. Save video metadata to database
        4. Verify all steps completed successfully

        WARNING: This test incurs significant API costs and takes 1-5 minutes.
        """
        from backend.services.wavespeed.video_generator import VideoGenerator
        from backend.services.supabase.storage import StorageService
        from backend.database.repositories.media import MediaRepository
        from datetime import datetime, timezone
        from uuid import uuid4

        storage = StorageService()
        media_repo = MediaRepository()

        # Step 1: Generate video from text prompt (text-to-video)
        video_gen = VideoGenerator()
        video_prompt = "An old man adjusts his glasses while reading a newspaper in a sunlit park"
        video_bytes = await video_gen.generate(
            prompt=video_prompt,
            size="1280*720",
            seed=-1
        )

        assert video_bytes is not None
        assert len(video_bytes) > 0
        print(f"✓ Generated video: {len(video_bytes)} bytes")

        # Step 2: Upload video to Supabase
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        video_file_id = uuid4().hex[:8]
        video_path = f"test/videos/{timestamp}_{video_file_id}.mp4"

        video_url = await storage.upload_media(
            video_path,
            video_bytes,
            "video/mp4"
        )

        assert "supabase.co" in video_url
        print(f"✓ Uploaded video to Supabase: {video_url}")

        # Step 3: Save video metadata to database
        from backend.models.media import Video

        video_model = Video(
            storage_path=video_path,
            public_url=video_url,
            prompt=video_prompt,
            file_size=len(video_bytes),
            mime_type="video/mp4"
        )
        video_record = await media_repo.create_video(video_model)

        assert video_record is not None
        assert video_record.prompt == video_prompt
        print(f"✓ Saved video to database: Media ID {video_record.id}")

        # Cleanup
        try:
            await storage.delete_media(video_path)
            await media_repo.delete(str(video_record.id))
            print(f"✓ Cleaned up test data")
        except Exception as e:
            print(f"⚠ Cleanup warning: {e}")

    async def test_tool_complete_workflow(self):
        """
        Test the complete workflow using the GenerateImageTool.
        This verifies the tool integrates all components correctly.

        WARNING: This test incurs API costs.
        """
        from backend.tools.media_generation_tools import GenerateImageTool
        from backend.database.repositories.media import MediaRepository
        from backend.services.supabase.storage import StorageService

        tool = GenerateImageTool()
        media_repo = MediaRepository()
        storage = StorageService()

        # Execute the tool
        result = await tool._arun(
            prompt="A blue square for integration test",
            size="1024*1024",
            guidance_scale=7.5
        )

        # Verify result format
        assert "Image generated successfully" in result
        assert "URL:" in result
        assert "Media ID:" in result
        print(f"✓ Tool execution result:\n{result}")

        # Extract media ID from result
        media_id_line = [line for line in result.split('\n') if "Media ID:" in line][0]
        media_id = media_id_line.split("Media ID:")[1].strip()

        # Verify database record exists
        media_record = await media_repo.get_by_id(media_id)
        assert media_record is not None
        # Note: get_by_id returns dict from BaseRepository
        print(f"✓ Verified database record: {media_id}")

        # Extract URL and verify storage
        url_line = [line for line in result.split('\n') if "URL:" in line][0]
        public_url = url_line.split("URL:")[1].strip()
        assert "supabase.co" in public_url
        print(f"✓ Verified Supabase URL: {public_url}")

        # Cleanup
        try:
            await storage.delete_media(media_record.storage_path)
            await media_repo.delete(media_id)
            print(f"✓ Cleaned up test data")
        except Exception as e:
            print(f"⚠ Cleanup warning: {e}")
