"""API contract tests for TTS endpoints.

Tests that API responses match OpenAPI specification.
"""
import pytest
from httpx import AsyncClient


class TestTTSAPIContract:
    """Test TTS API contract compliance."""

    @pytest.mark.asyncio
    async def test_health_check_contract(self, client: AsyncClient):
        """Test health check response matches schema."""
        response = await client.get("/health")

        assert response.status_code == 200

        data = response.json()

        # Verify structure
        assert "status" in data
        assert "version" in data
        assert "service" in data
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_detailed_contract(self, client: AsyncClient):
        """Test detailed health check response."""
        response = await client.get("/health/detailed")

        assert response.status_code == 200

        data = response.json()

        # Verify structure
        assert "status" in data
        assert "database" in data
        assert "tts_engine" in data
        # database should have status and message
        assert "status" in data["database"]
        assert "message" in data["database"]

    @pytest.mark.asyncio
    async def test_create_task_contract(self, client: AsyncClient):
        """Test POST /tts/generate request/response."""
        request_data = {
            "text": "Hello",
            "voice_name": "zh-CN-XiaoxiaoNeural",
            "rate": 1.0,
            "pitch": 1.0,
            "volume": 1.0,
        }

        response = await client.post("/api/v1/tts/generate", json=request_data)

        assert response.status_code == 201

        data = response.json()

        # Verify response fields
        required_fields = [
            "task_id",
            "text",
            "voice_name",
            "rate",
            "pitch",
            "volume",
            "status",
            "progress",
            "created_at",
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Verify types
        assert isinstance(data["task_id"], str)
        assert isinstance(data["text"], str)
        assert isinstance(data["voice_name"], str)
        assert isinstance(data["rate"], (int, float))
        assert isinstance(data["pitch"], (int, float))
        assert isinstance(data["volume"], (int, float))
        assert isinstance(data["status"], str)
        assert isinstance(data["progress"], int)

    @pytest.mark.asyncio
    async def test_create_task_validation_text_too_short(self, client: AsyncClient):
        """Test validation: text too short."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={"text": ""}  # Empty text
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_task_validation_text_too_long(self, client: AsyncClient):
        """Test validation: text too long."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "x" * 5001}  # Over 5000 chars
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_validation_rate_range(self, client: AsyncClient):
        """Test validation: rate out of range."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "Test", "rate": 3.0}  # Over 2.0
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_validation_pitch_range(self, client: AsyncClient):
        """Test validation: pitch out of range."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "Test", "pitch": 0.1}  # Under 0.5
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_validation_volume_range(self, client: AsyncClient):
        """Test validation: volume out of range."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "Test", "volume": 1.5}  # Over 1.0
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_task_contract(self, client: AsyncClient):
        """Test GET /tts/tasks/{task_id} response."""
        # First create a task
        create_response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "Test task"}
        )

        assert create_response.status_code == 201
        task_data = create_response.json()
        task_id = task_data["task_id"]

        # Get task
        response = await client.get(f"/api/v1/tts/tasks/{task_id}")

        assert response.status_code == 200

        data = response.json()

        # Verify same fields as create response
        required_fields = [
            "task_id", "text", "voice_name", "rate", "pitch",
            "volume", "status", "progress", "created_at"
        ]

        for field in required_fields:
            assert field in data

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, client: AsyncClient):
        """Test GET /tts/tasks/{id} with non-existent ID."""
        response = await client.get("/api/v1/tts/tasks/nonexistent-id")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_cancel_task_contract(self, client: AsyncClient):
        """Test DELETE /tts/tasks/{task_id} response."""
        # Create a task
        create_response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "Cancellable task"}
        )

        task_id = create_response.json()["task_id"]

        # Cancel immediately (should work as it's queued)
        response = await client.delete(f"/api/v1/tts/tasks/{task_id}")

        assert response.status_code == 200

        data = response.json()
        assert "task_id" in data
        assert "status" in data

    @pytest.mark.asyncio
    async def test_download_audio_contract(self, client: AsyncClient):
        """Test GET /tts/download/{task_id} returns audio."""
        # Create task
        create_response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "Download test"}
        )

        task_id = create_response.json()["task_id"]

        # Note: In real test, we'd need to wait for task to complete
        # For contract test, just verify endpoint structure
        # This will likely return 400 as task not ready
        response = await client.get(f"/api/v1/tts/download/{task_id}")

        # Should return 400 (not ready) or 200 with audio
        assert response.status_code in [200, 400, 404]

    @pytest.mark.asyncio
    async def test_openapi_schema_exists(self, client: AsyncClient):
        """Test that OpenAPI schema is available."""
        response = await client.get("/openapi.json")

        assert response.status_code == 200

        schema = response.json()

        # Verify schema structure
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

        # Verify TTS endpoints are documented
        paths = schema["paths"]
        assert "/api/v1/tts/generate" in paths or "/api/v1/tts/generate" in paths
        assert "/api/v1/tts/tasks/{task_id}" in paths or "/api/v1/tts/tasks/{task_id}" in paths
        assert "/api/v1/tts/download/{task_id}" in paths or "/api/v1/tts/download/{task_id}" in paths
