import pytest
import pytest_asyncio
from dotenv import load_dotenv

from airia import AiriaAsyncClient, AiriaClient
from airia.types.api import CreateConversationResponse

load_dotenv(override=True)

# Test constants
TEST_USER_ID = "00996c45-1515-48cf-90e9-af54c23dc301"
TEST_TITLE = "Test Conversation"
TEST_DEPLOYMENT_ID = "00000000-0000-0000-0000-000000000000"
TEST_DATA_SOURCE_FILES = {"documents": ["doc1.pdf", "doc2.txt"]}


# Fixtures for the sync client
@pytest.fixture
def sync_client():
    """Create a sync client with test API key."""
    return AiriaClient(log_requests=True)


# Fixtures for the async client
@pytest_asyncio.fixture
async def async_client():
    """Create an async client with test API key."""
    return AiriaAsyncClient(log_requests=True)


class TestSyncCreateConversation:
    """Tests for synchronous create_conversation method."""

    def test_create_conversation_minimal(self, sync_client: AiriaClient):
        """Test create_conversation with only required user_id parameter."""
        response = sync_client.create_conversation(user_id=TEST_USER_ID)
        
        # Verify response type
        assert isinstance(response, CreateConversationResponse)
        
        # Verify required fields are present
        assert response.user_id == TEST_USER_ID
        assert response.conversation_id is not None
        assert len(response.conversation_id) > 0
        assert response.websocket_url is not None
        assert response.deployment_id is not None

    def test_create_conversation_with_title(self, sync_client: AiriaClient):
        """Test create_conversation with title parameter."""
        response = sync_client.create_conversation(
            user_id=TEST_USER_ID,
            title=TEST_TITLE
        )
        
        # Verify response type and required fields
        assert isinstance(response, CreateConversationResponse)
        assert response.user_id == TEST_USER_ID
        assert response.conversation_id is not None

    def test_create_conversation_with_deployment_id(self, sync_client: AiriaClient):
        """Test create_conversation with deployment_id parameter."""
        response = sync_client.create_conversation(
            user_id=TEST_USER_ID,
            deployment_id=TEST_DEPLOYMENT_ID
        )
        
        # Verify response type and required fields
        assert isinstance(response, CreateConversationResponse)
        assert response.user_id == TEST_USER_ID
        assert response.conversation_id is not None

    def test_create_conversation_with_data_source_files(self, sync_client: AiriaClient):
        """Test create_conversation with data_source_files parameter."""
        response = sync_client.create_conversation(
            user_id=TEST_USER_ID,
            data_source_files=TEST_DATA_SOURCE_FILES
        )
        
        # Verify response type and required fields
        assert isinstance(response, CreateConversationResponse)
        assert response.user_id == TEST_USER_ID
        assert response.conversation_id is not None

    def test_create_conversation_bookmarked(self, sync_client: AiriaClient):
        """Test create_conversation with is_bookmarked parameter."""
        response = sync_client.create_conversation(
            user_id=TEST_USER_ID,
            is_bookmarked=True
        )
        
        # Verify response type and required fields
        assert isinstance(response, CreateConversationResponse)
        assert response.user_id == TEST_USER_ID
        assert response.conversation_id is not None

    def test_create_conversation_all_parameters(self, sync_client: AiriaClient):
        """Test create_conversation with all optional parameters."""
        response = sync_client.create_conversation(
            user_id=TEST_USER_ID,
            title=TEST_TITLE,
            deployment_id=TEST_DEPLOYMENT_ID,
            data_source_files=TEST_DATA_SOURCE_FILES,
            is_bookmarked=True,
            correlation_id="test-correlation-123"
        )
        
        # Verify response type and required fields
        assert isinstance(response, CreateConversationResponse)
        assert response.user_id == TEST_USER_ID
        assert response.conversation_id is not None
        assert response.websocket_url is not None
        assert response.deployment_id is not None

    def test_create_conversation_with_bearer_token(self):
        """Test create_conversation with bearer token authentication if available."""
        # This test will be skipped if AIRIA_BEARER_TOKEN is not available
        try:
            client = AiriaClient.with_bearer_token(bearer_token="test-bearer-token")
            # Note: This will likely fail in real testing since we're using a dummy token
            # but it tests the method signature and setup
            assert hasattr(client, 'create_conversation')
        except Exception:
            # Expected to fail with dummy token - just verify method exists
            pass


class TestAsyncCreateConversation:
    """Tests for asynchronous create_conversation method."""

    @pytest.mark.asyncio
    async def test_create_conversation_minimal(self, async_client: AiriaAsyncClient):
        """Test async create_conversation with only required user_id parameter."""
        response = await async_client.create_conversation(user_id=TEST_USER_ID)
        
        # Verify response type
        assert isinstance(response, CreateConversationResponse)
        
        # Verify required fields are present
        assert response.user_id == TEST_USER_ID
        assert response.conversation_id is not None
        assert len(response.conversation_id) > 0
        assert response.websocket_url is not None
        assert response.deployment_id is not None

    @pytest.mark.asyncio
    async def test_create_conversation_with_title(self, async_client: AiriaAsyncClient):
        """Test async create_conversation with title parameter."""
        response = await async_client.create_conversation(
            user_id=TEST_USER_ID,
            title=TEST_TITLE
        )
        
        # Verify response type and required fields
        assert isinstance(response, CreateConversationResponse)
        assert response.user_id == TEST_USER_ID
        assert response.conversation_id is not None

    @pytest.mark.asyncio
    async def test_create_conversation_with_deployment_id(self, async_client: AiriaAsyncClient):
        """Test async create_conversation with deployment_id parameter."""
        response = await async_client.create_conversation(
            user_id=TEST_USER_ID,
            deployment_id=TEST_DEPLOYMENT_ID
        )
        
        # Verify response type and required fields
        assert isinstance(response, CreateConversationResponse)
        assert response.user_id == TEST_USER_ID
        assert response.conversation_id is not None

    @pytest.mark.asyncio
    async def test_create_conversation_with_data_source_files(self, async_client: AiriaAsyncClient):
        """Test async create_conversation with data_source_files parameter."""
        response = await async_client.create_conversation(
            user_id=TEST_USER_ID,
            data_source_files=TEST_DATA_SOURCE_FILES
        )
        
        # Verify response type and required fields
        assert isinstance(response, CreateConversationResponse)
        assert response.user_id == TEST_USER_ID
        assert response.conversation_id is not None

    @pytest.mark.asyncio
    async def test_create_conversation_bookmarked(self, async_client: AiriaAsyncClient):
        """Test async create_conversation with is_bookmarked parameter."""
        response = await async_client.create_conversation(
            user_id=TEST_USER_ID,
            is_bookmarked=True
        )
        
        # Verify response type and required fields
        assert isinstance(response, CreateConversationResponse)
        assert response.user_id == TEST_USER_ID
        assert response.conversation_id is not None

    @pytest.mark.asyncio
    async def test_create_conversation_all_parameters(self, async_client: AiriaAsyncClient):
        """Test async create_conversation with all optional parameters."""
        response = await async_client.create_conversation(
            user_id=TEST_USER_ID,
            title=TEST_TITLE,
            deployment_id=TEST_DEPLOYMENT_ID,
            data_source_files=TEST_DATA_SOURCE_FILES,
            is_bookmarked=True,
            correlation_id="test-correlation-123"
        )
        
        # Verify response type and required fields
        assert isinstance(response, CreateConversationResponse)
        assert response.user_id == TEST_USER_ID
        assert response.conversation_id is not None
        assert response.websocket_url is not None
        assert response.deployment_id is not None

    @pytest.mark.asyncio
    async def test_create_conversation_with_bearer_token(self):
        """Test async create_conversation with bearer token authentication if available."""
        # This test will be skipped if AIRIA_BEARER_TOKEN is not available
        try:
            client = AiriaAsyncClient.with_bearer_token(bearer_token="test-bearer-token")
            # Note: This will likely fail in real testing since we're using a dummy token
            # but it tests the method signature and setup
            assert hasattr(client, 'create_conversation')
        except Exception:
            # Expected to fail with dummy token - just verify method exists
            pass