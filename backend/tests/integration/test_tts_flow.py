"""Integration tests for TTS API flow.

Tests complete end-to-end workflows with mocked edge-tts.
"""
import pytest
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient
from src.services.queue_service import queue_service


class TestTTSIntegration:
    """Test TTS API integration flows."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires running queue processor - tested in simpler integration tests")
    async def test_complete_tts_flow(self, client: AsyncClient, tmp_path):
        """Test complete TTS generation flow: create -> process -> download.

        Note: This test requires a running queue processor which is complex to set up
        in tests. The same functionality is tested in test_simple_integration.py.
        """
        # Mock edge-tts to avoid network calls and create actual files
        async def mock_save(file_path):
            # Create actual audio file
            from pathlib import Path
            Path(file_path).write_bytes(b"mock audio data for testing")

        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock(side_effect=mock_save)

        with patch("edge_tts.Communicate", return_value=mock_communicate):
            # Step 1: Create task
            create_response = await client.post(
                "/api/v1/tts/generate",
                json={
                    "text": "Complete flow test",
                    "voice_name": "zh-CN-XiaoxiaoNeural",
                }
            )

            assert create_response.status_code == 201
            task_data = create_response.json()
            task_id = task_data["task_id"]

            # Step 2: Wait for processing (background task)
            max_wait = 10  # seconds
            waited = 0
            interval = 0.5

            while waited < max_wait:
                await asyncio.sleep(interval)
                waited += interval

                # Check task status
                status_response = await client.get(f"/api/v1/tts/tasks/{task_id}")
                assert status_response.status_code == 200

                task = status_response.json()

                if task["status"] == "completed":
                    break
                elif task["status"] == "failed":
                    pytest.fail(f"Task failed: {task.get('error_message')}")

            # Should be completed by now
            status_response = await client.get(f"/api/v1/tts/tasks/{task_id}")
            task = status_response.json()

            assert task["status"] == "completed"
            assert task["progress"] == 100
            assert task["file_path"] is not None

            # Step 3: Download audio
            download_response = await client.get(f"/api/v1/tts/download/{task_id}")

            assert download_response.status_code == 200
            assert download_response.headers["content-type"] == "audio/mpeg"

            audio_data = download_response.content
            assert len(audio_data) > 0

    @pytest.mark.asyncio
    async def test_multiple_tasks_queue_processing(self, client: AsyncClient):
        """Test processing multiple tasks in queue."""
        # Ensure queue is empty before starting
        await queue_service.clear_queue()

        # Mock edge-tts
        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock()

        with patch("edge_tts.Communicate", return_value=mock_communicate):
            # Create multiple tasks
            task_ids = []

            for i in range(3):
                response = await client.post(
                    "/api/v1/tts/generate",
                    json={"text": f"Task {i}"}
                )

                assert response.status_code == 201
                task_ids.append(response.json()["task_id"])

            # All tasks should be in queue or processing
            for task_id in task_ids:
                response = await client.get(f"/api/v1/tts/tasks/{task_id}")
                task = response.json()

                assert task["status"] in ["queued", "processing", "completed"]

    @pytest.mark.asyncio
    async def test_task_creation_with_all_params(self, client: AsyncClient, tmp_path):
        """Test task creation with all parameters."""
        # Ensure queue is empty before starting
        await queue_service.clear_queue()

        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock()

        with patch("edge_tts.Communicate", return_value=mock_communicate):
            response = await client.post(
                "/api/v1/tts/generate",
                json={
                    "text": "Full params test",
                    "voice_name": "zh-CN-YunyangNeural",
                    "rate": 1.5,
                    "pitch": 0.8,
                    "volume": 0.9,
                }
            )

            assert response.status_code == 201

            task = response.json()

            assert task["text"] == "Full params test"
            assert task["voice_name"] == "zh-CN-YunyangNeural"
            assert task["rate"] == 1.5
            assert task["pitch"] == 0.8
            assert task["volume"] == 0.9

    @pytest.mark.asyncio
    async def test_task_not_found_error(self, client: AsyncClient):
        """Test error handling for non-existent task."""
        response = await client.get("/api/v1/tts/tasks/nonexistent-id")

        assert response.status_code == 404

        error = response.json()
        assert "detail" in error

    @pytest.mark.asyncio
    async def test_invalid_voice_name(self, client: AsyncClient):
        """Test validation of invalid voice name."""
        response = await client.post(
            "/api/v1/tts/generate",
            json={
                "text": "Test",
                "voice_name": "invalid-voice-name",
            }
        )

        # Pydantic validation errors return 422, not 400
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_text_sanitization(self, client: AsyncClient):
        """Test that input text is sanitized."""
        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock()

        with patch("edge_tts.Communicate", return_value=mock_communicate):
            # Text with path traversal attempt
            response = await client.post(
                "/api/v1/tts/generate",
                json={
                    "text": "../../../etc/passwd",
                }
            )

            # Should be rejected
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_default_parameters(self, client: AsyncClient, tmp_path):
        """Test that default parameters are applied."""
        # Ensure queue is empty before starting
        await queue_service.clear_queue()

        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock()

        with patch("edge_tts.Communicate", return_value=mock_communicate):
            # Create task with minimal params
            response = await client.post(
                "/api/v1/tts/generate",
                json={
                    "text": "Defaults test",
                }
            )

            assert response.status_code == 201

            task = response.json()

            # Check defaults
            assert task["voice_name"] == "zh-CN-XiaoxiaoNeural"
            assert task["rate"] == 1.0
            assert task["pitch"] == 1.0
            assert task["volume"] == 1.0

    @pytest.mark.asyncio
    async def test_cancel_queued_task(self, client: AsyncClient):
        """Test cancelling a queued task."""
        # Ensure queue is empty before starting
        await queue_service.clear_queue()

        # Create task
        create_response = await client.post(
            "/api/v1/tts/generate",
            json={"text": "Cancel test"}
        )

        task_id = create_response.json()["task_id"]

        # Cancel immediately (should be queued)
        cancel_response = await client.delete(f"/api/v1/tts/tasks/{task_id}")

        assert cancel_response.status_code == 200

        # Verify cancelled status
        status_response = await client.get(f"/api/v1/tts/tasks/{task_id}")
        task = status_response.json()

        assert task["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_database_persistence(self, client: AsyncClient, tmp_path, test_db):
        """Test that tasks are persisted to database."""
        # Ensure queue is empty before starting
        await queue_service.clear_queue()

        from src.models.task import Task
        from sqlalchemy import select

        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock()

        with patch("edge_tts.Communicate", return_value=mock_communicate):
            # Create task via API
            api_response = await client.post(
                "/api/v1/tts/generate",
                json={"text": "Persistence test"}
            )

            task_id = api_response.json()["task_id"]

            # Query database directly
            result = await test_db.execute(
                select(Task).where(Task.task_id == task_id)
            )
            db_task = result.scalar_one_or_none()

            assert db_task is not None
            assert db_task.text == "Persistence test"
            assert db_task.task_id == task_id
