from unittest.mock import patch

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from airia import AiriaAsyncClient, AiriaClient
from airia.exceptions import AiriaAPIError

# Load environment variables from .env file
load_dotenv(override=True)

# Test constants
SAMPLE_PROJECTS = {
    "items": [
        {
            "tenantId": "2ce49ae0-c3ff-421a-91b7-830d0c73b348",
            "createdAt": "2025-01-22T20:00:19.8504590Z",
            "requireClassification": False,
            "budgetAmount": None,
            "budgetPeriod": None,
            "budgetAlert": None,
            "budgetStop": False,
            "usedBudgetAmount": None,
            "resumeEndsAt": None,
            "updatedAt": "2025-01-22T20:00:19.8509410Z",
            "pipelines": [
                {
                    "id": "940275e2-7eae-4bc9-9830-4ef595727b87",
                    "name": "Cloudkit Records",
                },
                {"id": "b8c24cc9-39de-4e76-b7dd-debac381d1a8", "name": "RAG_test"},
                {
                    "id": "17554b31-2370-4d2d-91de-4fe4805b9ef9",
                    "name": "Omni Agent - Test Agent to be Described",
                },
            ],
            "models": None,
            "dataSources": [],
            "prompts": None,
            "apiKeys": None,
            "memories": None,
            "projectIcon": "https://airiaimagesprod.blob.core.windows.net/airia-default/8a8f75f5-bd6c-470b-bf23-e82c58d81912?sv=2025-05-05&spr=https&st=2025-06-17T20%3A23%3A39Z&se=2025-06-18T20%3A23%3A39Z&sr=b&sp=r&sig=TE7B5sgtCp%2BMpeQizbuhZShOXRcGPol%2BGitQdKGDBKg%3D",
            "projectIconId": "8a8f75f5-bd6c-470b-bf23-e82c58d81912",
            "description": "Agents Developed by AI Core Team",
            "projectType": "Standard",
            "classifications": None,
            "id": "01948f99-f78a-7415-a187-b250c6e04458",
            "name": "AI Core",
        }
    ],
    "totalCount": 1,
}


@pytest.fixture
def sync_client():
    return AiriaClient(log_requests=True)


@pytest_asyncio.fixture
async def async_client():
    return AiriaAsyncClient(log_requests=True)


class TestSyncGetProjectsIds:
    """Test cases for synchronous get_projects method."""

    def test_get_projects_success(self, sync_client: AiriaClient):
        """Test successful retrieval of projectss."""
        with patch.object(sync_client, "_make_request") as mock_request:
            mock_request.return_value = SAMPLE_PROJECTS

            result = sync_client.get_projects()

            assert isinstance(result, list)
            assert len(result) == 1
            mock_request.assert_called_once()

    def test_get_projects_empty_dict(self, sync_client: AiriaClient):
        """Test handling of empty project response."""
        with patch.object(sync_client, "_make_request") as mock_request:
            mock_request.return_value = {}

            result = sync_client.get_projects()

            assert result == []
            assert isinstance(result, list)
            assert len(result) == 0

    def test_get_projects_with_correlation_id(self, sync_client: AiriaClient):
        """Test using custom correlation ID."""
        custom_correlation_id = "test-correlation-123"

        with patch.object(sync_client, "_make_request") as mock_request:
            mock_request.return_value = SAMPLE_PROJECTS

            result = sync_client.get_projects(correlation_id=custom_correlation_id)

            assert isinstance(result, list)
            assert len(result) == 1
            mock_request.assert_called_once()

    def test_get_projects_api_error(self, sync_client: AiriaClient):
        """Test error handling for API errors."""
        with patch.object(sync_client, "_make_request") as mock_request:
            mock_request.side_effect = AiriaAPIError(
                status_code=404, message="Projects not found"
            )

            with pytest.raises(AiriaAPIError) as exc_info:
                sync_client.get_projects()

            assert "Projects not found" in str(exc_info.value)
            assert exc_info.value.status_code == 404


class TestAsyncGetActivePipelineIds:
    """Test cases for asynchronous get_active_pipelines_ids method."""

    @pytest.mark.asyncio
    async def test_get_projects_success(self, async_client: AiriaAsyncClient):
        """Test successful retrieval of projects."""
        with patch.object(async_client, "_make_request") as mock_request:
            mock_request.return_value = SAMPLE_PROJECTS

            result = await async_client.get_projects()

            assert isinstance(result, list)
            assert len(result) == 1
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_projects_empty_list(self, async_client: AiriaAsyncClient):
        """Test handling of empty project list response."""
        with patch.object(async_client, "_make_request") as mock_request:
            mock_request.return_value = []

            result = await async_client.get_projects()

            assert result == []
            assert isinstance(result, list)
            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_projects_with_custom_params(
        self, async_client: AiriaAsyncClient
    ):
        """Test using custom API version and correlation ID."""
        custom_correlation_id = "async-test-correlation-456"

        with patch.object(async_client, "_make_request") as mock_request:
            mock_request.return_value = SAMPLE_PROJECTS

            result = await async_client.get_projects(
                correlation_id=custom_correlation_id
            )

            assert isinstance(result, list)
            assert len(result) == 1
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_projects_api_error(
        self, async_client: AiriaAsyncClient
    ):
        """Test error handling for API errors."""
        with patch.object(async_client, "_make_request") as mock_request:
            mock_request.side_effect = AiriaAPIError(
                status_code=403, message="Access forbidden"
            )

            with pytest.raises(AiriaAPIError) as exc_info:
                await async_client.get_projects()

            assert "Access forbidden" in str(exc_info.value)
            assert exc_info.value.status_code == 403
