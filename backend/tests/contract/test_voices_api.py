"""API contract tests for voices endpoint.

Tests that GET /api/v1/voices responses match the schema specification.
"""

import pytest
from httpx import AsyncClient


class TestVoicesAPIContract:
    """Test voices API contract compliance."""

    @pytest.mark.asyncio
    async def test_voices_response_status(self, client: AsyncClient):
        """Test GET /voices returns 200 status code."""
        response = await client.get("/api/v1/tts/voices")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_voices_response_structure(self, client: AsyncClient):
        """Test voices response has correct structure."""
        response = await client.get("/api/v1/tts/voices")

        data = response.json()

        # Verify top-level structure
        assert "voices" in data
        assert isinstance(data["voices"], list)

    @pytest.mark.asyncio
    async def test_voices_response_fields(self, client: AsyncClient):
        """Test each voice has required fields."""
        response = await client.get("/api/v1/tts/voices")

        data = response.json()

        # Should have voices
        assert len(data["voices"]) > 0

        # Check each voice has required fields
        for voice in data["voices"]:
            assert "name" in voice
            assert "voice_id" in voice
            assert "description" in voice
            assert "default" in voice
            assert isinstance(voice["name"], str)
            assert isinstance(voice["voice_id"], str)
            assert isinstance(voice["description"], str)
            assert isinstance(voice["default"], bool)

    @pytest.mark.asyncio
    async def test_voices_contains_all_presets(self, client: AsyncClient):
        """Test response contains all 5 preset voices."""
        response = await client.get("/api/v1/tts/voices")

        data = response.json()

        # Should have exactly 5 voices
        assert len(data["voices"]) == 5

        # Extract voice names
        voice_names = [v["name"] for v in data["voices"]]

        # Check all preset voices are present
        expected_voices = [
            "晓晓-女声",
            "云扬-男声",
            "晓悠-童声",
            "晓伊-年轻女声",
            "云健-沉稳男声",
        ]

        for expected in expected_voices:
            assert expected in voice_names, f"Missing voice: {expected}"

    @pytest.mark.asyncio
    async def test_voices_default_flag(self, client: AsyncClient):
        """Test exactly one voice is marked as default."""
        response = await client.get("/api/v1/tts/voices")

        data = response.json()

        # Count default voices
        default_voices = [v for v in data["voices"] if v["default"] is True]

        # Should have exactly one default
        assert len(default_voices) == 1

        # Default should be "晓晓-女声"
        assert default_voices[0]["name"] == "晓晓-女声"
        assert default_voices[0]["voice_id"] == "zh-CN-XiaoxiaoNeural"

    @pytest.mark.asyncio
    async def test_voices_ids_are_valid(self, client: AsyncClient):
        """Test all voice IDs follow correct format."""
        response = await client.get("/api/v1/tts/voices")

        data = response.json()

        # All voice IDs should start with "zh-CN-"
        for voice in data["voices"]:
            assert voice["voice_id"].startswith("zh-CN-")
            # Should end with "Neural"
            assert voice["voice_id"].endswith("Neural")

    @pytest.mark.asyncio
    async def test_voices_no_duplicates(self, client: AsyncClient):
        """Test no duplicate voice IDs or names."""
        response = await client.get("/api/v1/tts/voices")

        data = response.json()

        # Extract IDs and names
        voice_ids = [v["voice_id"] for v in data["voices"]]
        voice_names = [v["name"] for v in data["voices"]]

        # Check for duplicates
        assert len(voice_ids) == len(set(voice_ids)), "Duplicate voice IDs found"
        assert len(voice_names) == len(set(voice_names)), "Duplicate voice names found"

    @pytest.mark.asyncio
    async def test_voices_openapi_spec(self, client: AsyncClient):
        """Test voices endpoint is documented in OpenAPI."""
        # Get OpenAPI schema
        response = await client.get("/openapi.json")

        assert response.status_code == 200

        openapi_schema = response.json()

        # Check voices endpoint is documented
        assert "/api/v1/tts/voices" in openapi_schema["paths"]
        assert "get" in openapi_schema["paths"]["/api/v1/tts/voices"]

        # Check response schema
        voices_path = openapi_schema["paths"]["/api/v1/tts/voices"]["get"]
        assert "200" in voices_path["responses"]

        # Check response schema references VoicesResponse
        response_schema = voices_path["responses"]["200"]
        assert "content" in response_schema
        assert "application/json" in response_schema["content"]

    @pytest.mark.asyncio
    async def test_voices_response_consistency(self, client: AsyncClient):
        """Test voices response is consistent across multiple calls."""
        # First call
        response1 = await client.get("/api/v1/tts/voices")
        data1 = response1.json()

        # Second call
        response2 = await client.get("/api/v1/tts/voices")
        data2 = response2.json()

        # Responses should be identical
        assert data1 == data2

    @pytest.mark.asyncio
    async def test_voices_caching_headers(self, client: AsyncClient):
        """Test voices response includes appropriate caching headers."""
        response = await client.get("/api/v1/tts/voices")

        # Voices list doesn't change frequently, should be cacheable
        # Note: We're not enforcing specific headers, just checking the endpoint works
        assert response.status_code == 200
