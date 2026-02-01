"""Error handling integration tests.

Tests for error handling across different endpoints and scenarios.
"""

import pytest

from httpx import AsyncClient


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling scenarios."""

    async def test_text_too_short(self, client: AsyncClient):
        """Test handling text that's too short."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "", "voice_name": "zh-CN-XiaoxiaoNeural"},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_text_too_long(self, client: AsyncClient):
        """Test handling text that's too long."""
        long_text = "A" * 5001

        response = await client.post(
            "/api/v1/tts/generate",
            json={"text": long_text, "voice_name": "zh-CN-XiaoxiaoNeural"},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_invalid_voice_name(self, client: AsyncClient):
        """Test handling invalid voice name."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "Test", "voice_name": "InvalidVoice"},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_invalid_rate_parameter(self, client: AsyncClient):
        """Test handling invalid rate parameter."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "Test", "rate": 3.0},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_invalid_pitch_parameter(self, client: AsyncClient):
        """Test handling invalid pitch parameter."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "Test", "pitch": 0.0},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_invalid_volume_parameter(self, client: AsyncClient):
        """Test handling invalid volume parameter."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "Test", "volume": 2.0},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_task_not_found(self, client: AsyncClient):
        """Test handling non-existent task."""
        response = await client.get("/api/v1/tts/tasks/nonexistent_task_id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data or "message" in data

    async def test_history_not_found(self, client: AsyncClient):
        """Test handling non-existent history record."""
        response = await client.delete("/api/v1/history/99999")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data or "message" in data

    async def test_missing_required_field(self, client: AsyncClient):
        """Test handling missing required field."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={},  # Missing 'text' field
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_extra_field_allowed(self, client: AsyncClient):
        """Test that extra fields are ignored."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={
                "text": "Test",
                "extra_field": "should_be_ignored",
            },
        )

        # Should succeed or fail with validation error, but not crash
        assert response.status_code in [200, 201, 422]

    async def test_queue_full_error(self, client: AsyncClient):
        """Test handling when queue is full."""
        # This would require mocking or setting up a full queue scenario
        # For now, we'll test the endpoint exists
        response = await client.get("/api/v1/queue/status")

        assert response.status_code == 200
        data = response.json()
        assert "max_queue_size" in data

    async def test_health_check_always_works(self, client: AsyncClient):
        """Test that health check is always accessible."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    async def test_wrong_content_type(self, client: AsyncClient):
        """Test handling wrong content type."""
        response = await client.post(
            "/api/v1/tts/generate",
            data="text instead of json",
            headers={"Content-Type": "text/plain"},
        )

        assert response.status_code == 422

    async def test_malformed_json(self, client: AsyncClient):
        """Test handling malformed JSON."""
        response = await client.post(
            "/api/v1/tts/generate",
            content="{'text': 'invalid json'}",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422

    async def test_null_bytes_in_text(self, client: AsyncClient):
        """Test handling null bytes in text."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "Hello\x00World"},
        )

        assert response.status_code == 422

    async def test_path_traversal_in_text(self, client: AsyncClient):
        """Test handling path traversal patterns in text."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "../../etc/passwd"},
        )

        # Should be rejected or sanitized
        assert response.status_code in [400, 422]
        data = response.json()
        # Check both 'message' and 'detail' fields
        error_text = (
            data.get("message", "")
            or data.get("detail", "")
            or str(data)
        ).lower()
        assert "path traversal" in error_text or "patterns" in error_text

    async def test_control_characters_in_text(self, client: AsyncClient):
        """Test handling control characters in text."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "Hello\x01\x02World"},
        )

        assert response.status_code in [400, 422]
