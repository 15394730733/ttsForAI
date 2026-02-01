"""API contract tests for history endpoint.

Tests that history API responses match the schema specification.
"""

import pytest
from httpx import AsyncClient


class TestHistoryAPIContract:
    """Test history API contract compliance."""

    @pytest.mark.asyncio
    async def test_get_history_response_status(self, client: AsyncClient):
        """Test GET /history returns 200 status code."""
        response = await client.get("/api/v1/history/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_get_history_response_structure(self, client: AsyncClient):
        """Test history list response has correct structure."""
        response = await client.get("/api/v1/history/")

        data = response.json()

        # Verify top-level structure
        assert "records" in data
        assert "total" in data
        assert isinstance(data["records"], list)
        assert isinstance(data["total"], int)

    @pytest.mark.asyncio
    async def test_history_record_fields(self, client: AsyncClient):
        """Test each history record has required fields."""
        response = await client.get("/api/v1/history/")

        data = response.json()

        # Check each record has required fields (if any exist)
        for record in data["records"]:
            assert "id" in record
            assert "task_id" in record
            assert "text_summary" in record
            assert "voice_params" in record
            assert "created_at" in record
            assert "file_path" in record
            assert "file_size" in record
            assert "status" in record

            # Check types
            assert isinstance(record["id"], int)
            assert isinstance(record["task_id"], str)
            assert isinstance(record["text_summary"], str)
            assert isinstance(record["voice_params"], str)
            assert isinstance(record["created_at"], str)
            assert isinstance(record["file_path"], str)
            assert isinstance(record["file_size"], int)
            assert isinstance(record["status"], str)

    @pytest.mark.asyncio
    async def test_history_pagination(self, client: AsyncClient):
        """Test history pagination parameters work."""
        # Test limit
        response = await client.get("/api/v1/history/?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["records"]) <= 5

        # Test skip
        response = await client.get("/api/v1/history/?skip=2")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_history_default_limit(self, client: AsyncClient):
        """Test history has default limit of 20."""
        response = await client.get("/api/v1/history/")

        data = response.json()

        # Should not exceed default limit
        assert len(data["records"]) <= 20

    @pytest.mark.asyncio
    async def test_history_openapi_spec(self, client: AsyncClient):
        """Test history endpoints are documented in OpenAPI."""
        # Get OpenAPI schema
        response = await client.get("/openapi.json")

        assert response.status_code == 200

        openapi_schema = response.json()

        # Check GET /history is documented
        assert "/api/v1/history/" in openapi_schema["paths"]
        assert "get" in openapi_schema["paths"]["/api/v1/history/"]

        # Check DELETE /history/{id} is documented
        assert "/api/v1/history/{history_id}" in openapi_schema["paths"]
        assert "delete" in openapi_schema["paths"]["/api/v1/history/{history_id}"]

        # Check DELETE /history/clear is documented
        assert "/api/v1/history/clear" in openapi_schema["paths"]
        assert "delete" in openapi_schema["paths"]["/api/v1/history/clear"]

    @pytest.mark.asyncio
    async def test_delete_history_not_found(self, client: AsyncClient):
        """Test DELETE /history/{id} with non-existent ID returns 404."""
        response = await client.delete("/api/v1/history/99999")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_clear_history_response_status(self, client: AsyncClient):
        """Test DELETE /history/clear returns 200 status code."""
        response = await client.delete("/api/v1/history/clear")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_clear_history_response_structure(self, client: AsyncClient):
        """Test clear history response has correct structure."""
        response = await client.delete("/api/v1/history/clear")

        data = response.json()

        # Verify response structure
        assert "deleted_count" in data
        assert "message" in data
        assert isinstance(data["deleted_count"], int)
        assert isinstance(data["message"], str)
        assert data["deleted_count"] >= 0

    @pytest.mark.asyncio
    async def test_delete_history_response_structure(self, client: AsyncClient):
        """Test delete history record response has correct structure."""
        # First, this will likely return 404 if no records exist, but we can test the response format
        response = await client.delete("/api/v1/history/1")

        # If 404, test that response
        if response.status_code == 404:
            detail = response.json()
            assert "detail" in detail
        # If 200 (record existed), test success response
        elif response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "deleted" in data
            assert "message" in data
