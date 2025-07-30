"""Tests for LINE Messaging API client."""

from unittest.mock import AsyncMock, patch

import pytest

from line_api.core import LineAPIConfig, LineMessageError
from line_api.messaging import LineMessagingClient, TextMessage


@pytest.fixture
def config() -> LineAPIConfig:
    """Create test configuration."""
    return LineAPIConfig(
        channel_access_token="test_token",
        channel_secret="test_secret",
        login_channel_id=None,
        login_channel_secret=None,
        liff_channel_id=None,
        api_base_url="https://api.line.me/v2/bot",
        timeout=30.0,
        max_retries=3,
        retry_delay=1.0,
        debug=False,
    )


@pytest.fixture
def client(config: LineAPIConfig) -> LineMessagingClient:
    """Create test client."""
    return LineMessagingClient(config)


@pytest.mark.asyncio
async def test_push_message_success(client: LineMessagingClient) -> None:
    """Test successful push message."""
    messages = [TextMessage.create("Hello, World!")]

    with patch.object(client, "_make_request", new=AsyncMock()) as mock_request:
        mock_request.return_value = {}

        result = await client.push_message("user123", messages)

        assert result is True
        mock_request.assert_called_once()

        # Verify the request data
        call_args = mock_request.call_args
        assert call_args[0] == ("POST", "message/push")
        request_data = call_args[1]["data"]
        assert request_data["to"] == "user123"
        assert len(request_data["messages"]) == 1
        assert request_data["messages"][0]["type"] == "text"
        assert request_data["messages"][0]["text"] == "Hello, World!"


@pytest.mark.asyncio
async def test_push_message_validation(client: LineMessagingClient) -> None:
    """Test push message validation."""
    # Test empty messages
    with pytest.raises(LineMessageError, match="At least one message is required"):
        await client.push_message("user123", [])

    # Test too many messages
    messages = [TextMessage.create(f"Message {i}") for i in range(6)]
    with pytest.raises(LineMessageError, match="Maximum 5 messages allowed"):
        await client.push_message("user123", messages)


@pytest.mark.asyncio
async def test_multicast_message_validation(client: LineMessagingClient) -> None:
    """Test multicast message validation."""
    messages = [TextMessage.create("Hello")]

    # Test empty user IDs
    with pytest.raises(LineMessageError, match="At least one user ID is required"):
        await client.multicast_message([], messages)

    # Test too many user IDs
    user_ids = [f"user{i}" for i in range(501)]
    with pytest.raises(LineMessageError, match="Maximum 500 recipients allowed"):
        await client.multicast_message(user_ids, messages)


@pytest.mark.asyncio
async def test_reply_message_validation(client: LineMessagingClient) -> None:
    """Test reply message validation."""
    # Test empty messages
    with pytest.raises(LineMessageError, match="At least one message is required"):
        await client.reply_message("reply_token", [])


@pytest.mark.asyncio
async def test_client_context_manager(config: LineAPIConfig) -> None:
    """Test client as context manager."""
    async with LineMessagingClient(config) as client:
        assert client is not None
        # Client should be properly initialized
        assert client.config == config
