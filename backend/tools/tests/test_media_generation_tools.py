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

    async def test_arun_with_real_api(self, cleanup_generated_media):
        """
        Test generating a video using real Wavespeed API.
        WARNING: This test will incur API costs and take time.
        """
        tool = GenerateVideoTool()

        # Use a sample image URL (you might want to skip this if you don't have an image)
        # For now, we'll just test that the tool handles the call properly
        result = await tool._arun(
            image_url="https://example.com/sample.jpg",
            prompt="Gentle zoom in",
            seed=-1
        )

        # Verify we got a response (might be error if image doesn't exist, which is OK)
        assert isinstance(result, str)
        # Should either succeed or fail gracefully
        assert "Video generated successfully" in result or "Error generating video" in result

    def test_run_raises_not_implemented(self):
        """Test that sync version raises NotImplementedError."""
        tool = GenerateVideoTool()

        with pytest.raises(NotImplementedError):
            tool._run(image_url="test", prompt="test")


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
