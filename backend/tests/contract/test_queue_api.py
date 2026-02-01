"""API contract tests for queue endpoint.

Tests that GET /api/v1/queue/status responses match the schema specification.
"""

import pytest
from httpx import AsyncClient


class TestQueueAPIContract:
    """Test queue API contract compliance."""

    @pytest.mark.asyncio
    async def test_queue_status_response_status(self, client: AsyncClient):
        """Test GET /queue/status returns 200 status code."""
        response = await client.get("/api/v1/queue/status")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_queue_status_response_structure(self, client: AsyncClient):
        """Test queue status response has correct structure."""
        response = await client.get("/api/v1/queue/status")

        data = response.json()

        # Verify required fields
        assert "queued_count" in data
        assert "processing_count" in data
        assert "completed_count" in data
        assert "max_queue_size" in data
        assert "current_task" in data

    @pytest.mark.asyncio
    async def test_queue_status_field_types(self, client: AsyncClient):
        """Test queue status response fields have correct types."""
        response = await client.get("/api/v1/queue/status")

        data = response.json()

        # Check types
        assert isinstance(data["queued_count"], int)
        assert isinstance(data["processing_count"], int)
        assert isinstance(data["completed_count"], int)
        assert isinstance(data["max_queue_size"], int)
        # current_task can be None or an object
        assert data["current_task"] is None or isinstance(data["current_task"], dict)

    @pytest.mark.asyncio
    async def test_queue_status_values_are_valid(self, client: AsyncClient):
        """Test queue status values are within valid ranges."""
        response = await client.get("/api/v1/queue/status")

        data = response.json()

        # Counts should be non-negative
        assert data["queued_count"] >= 0
        assert data["processing_count"] >= 0
        assert data["completed_count"] >= 0

        # Max queue size should be positive
        assert data["max_queue_size"] > 0

        # Queued count should not exceed max
        assert data["queued_count"] <= data["max_queue_size"]

    @pytest.mark.asyncio
    async def test_queue_status_openapi_spec(self, client: AsyncClient):
        """Test queue status endpoint is documented in OpenAPI."""
        # Get OpenAPI schema
        response = await client.get("/openapi.json")

        assert response.status_code == 200

        openapi_schema = response.json()

        # Check endpoint is documented
        assert "/api/v1/queue/status" in openapi_schema["paths"]
        assert "get" in openapi_schema["paths"]["/api/v1/queue/status"]

        # Check response schema
        queue_path = openapi_schema["paths"]["/api/v1/queue/status"]["get"]
        assert "200" in queue_path["responses"]

    @pytest.mark.asyncio
    async def test_queue_status_consistency(self, client: AsyncClient):
        """Test queue status response is consistent across multiple calls."""
        # First call
        response1 = await client.get("/api/v1/queue/status")
        data1 = response1.json()

        # Second call (should have same structure)
        response2 = await client.get("/api/v1/queue/status")
        data2 = response2.json()

        # Should have same structure
        assert set(data1.keys()) == set(data2.keys())

        # Max queue size should be constant
        assert data1["max_queue_size"] == data2["max_queue_size"]
