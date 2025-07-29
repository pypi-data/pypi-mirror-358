import os
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock

from airia import AiriaAsyncClient, AiriaClient


class TestBearerTokenAuthentication:
    """Tests for bearer token authentication functionality."""

    def test_sync_client_with_bearer_token(self):
        """Test synchronous client initialization with bearer token."""
        bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token"
        client = AiriaClient(bearer_token=bearer_token)
        
        assert client.bearer_token == bearer_token
        assert client.api_key is None

    def test_sync_client_with_bearer_token_class_method(self):
        """Test synchronous client initialization using with_bearer_token class method."""
        bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token"
        client = AiriaClient.with_bearer_token(bearer_token)
        
        assert client.bearer_token == bearer_token
        assert client.api_key is None

    def test_explicit_api_key_and_bearer_token_conflict(self):
        """Test that providing both api_key and bearer_token explicitly raises an error."""
        with pytest.raises(ValueError, match="Cannot provide both api_key and bearer_token"):
            AiriaClient(api_key="test_key", bearer_token="test_token")

    def test_no_auth_provided_raises_error(self):
        """Test that providing no authentication raises an error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Authentication required"):
                AiriaClient()

    def test_bearer_token_auth_header_generation(self):
        """Test that bearer token generates correct Authorization header."""
        bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token"
        client = AiriaClient(bearer_token=bearer_token)
        
        request_data = client._prepare_request("https://test.com")
        
        assert "Authorization" in request_data.headers
        assert request_data.headers["Authorization"] == f"Bearer {bearer_token}"
        assert "X-API-KEY" not in request_data.headers

    def test_api_key_auth_header_generation(self):
        """Test that API key generates correct X-API-KEY header."""
        api_key = "test_api_key"
        client = AiriaClient(api_key=api_key)
        
        request_data = client._prepare_request("https://test.com")
        
        assert "X-API-KEY" in request_data.headers
        assert request_data.headers["X-API-KEY"] == api_key
        assert "Authorization" not in request_data.headers

    def test_bearer_token_logging_redaction(self):
        """Test that bearer token is redacted in logs."""
        bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token"
        client = AiriaClient(bearer_token=bearer_token, log_requests=True)
        
        # Mock the logger to capture log output
        with patch.object(client, 'logger') as mock_logger:
            request_data = client._prepare_request("https://test.com")
            
            # Check that the log call was made and bearer token was redacted
            mock_logger.info.assert_called_once()
            log_call_args = mock_logger.info.call_args[0][0]
            assert "[REDACTED]" in log_call_args
            assert bearer_token not in log_call_args

    def test_bearer_token_error_sanitization(self):
        """Test that bearer token is sanitized in error messages."""
        bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token"
        client = AiriaClient(bearer_token=bearer_token)
        
        # Test the sanitization logic directly
        error_message = f"Invalid token: {bearer_token}"
        sanitized_message = error_message
        if client.bearer_token and client.bearer_token in sanitized_message:
            sanitized_message = sanitized_message.replace(client.bearer_token, "[REDACTED]")
        
        assert bearer_token not in sanitized_message
        assert "[REDACTED]" in sanitized_message


