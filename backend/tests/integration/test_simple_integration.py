"""Simple integration tests for TTS API.

Tests basic API endpoints without complex queue processing.
"""
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import logging

from httpx import AsyncClient

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)


class TestSimpleIntegration:
    """Test TTS API with simple scenarios."""

    @pytest.mark.asyncio
    async def test_create_task_endpoint(self, client: AsyncClient):
        """Test task creation endpoint."""
        # Mock queue service to avoid background processing
        with patch("src.api.tts.queue_service") as mock_queue:
            mock_queue.is_full.return_value = False
            mock_queue.enqueue = AsyncMock(return_value=True)

            response = await client.post(
                "/api/v1/tts/generate",
                json={
                    "text": "Test text",
                    "voice_name": "zh-CN-XiaoxiaoNeural",
                }
            )

            # Print response for debugging
            if response.status_code != 201:
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")

            assert response.status_code == 201
            data = response.json()
            assert "task_id" in data
            assert data["status"] == "queued"
            assert data["text"] == "Test text"

    @pytest.mark.asyncio
    async def test_create_task_validation(self, client: AsyncClient):
        """Test input validation."""
        # Test empty text
        response = await client.post(
            "/api/v1/tts/generate",
            json={
                "text": "",
                "voice_name": "zh-CN-XiaoxiaoNeural",
            }
        )
        assert response.status_code == 422

        # Test rate out of range
        response = await client.post(
            "/api/v1/tts/generate",
            json={
                "text": "Test",
                "voice_name": "zh-CN-XiaoxiaoNeural",
                "rate": 3.0,  # Invalid: max is 2.0
            }
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, client: AsyncClient):
        """Test getting non-existent task."""
        response = await client.get("/api/v1/tts/tasks/nonexistent-id")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
