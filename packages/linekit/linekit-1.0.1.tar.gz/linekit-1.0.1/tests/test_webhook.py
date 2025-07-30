"""
Tests for LINE Webhook functionality.

This module contains comprehensive tests for webhook handling,
signature verification, and event processing.
"""

import base64
import hashlib
import hmac
from unittest.mock import patch

import pytest

from line_api.core.config import LineAPIConfig
from line_api.webhook import (
    LineDeliveryContext,
    LineEventSource,
    LineMessageEvent,
    LineTextMessage,
    LineWebhookHandler,
    LineWebhookPayload,
    SignatureVerificationError,
    safe_verify_webhook_signature,
    verify_webhook_signature,
)


class TestSignatureVerification:
    """Test signature verification functionality."""

    def test_verify_webhook_signature_valid(self):
        """Test that valid signatures are accepted."""
        body = b'{"test": "data"}'
        secret = "test_secret"

        # Create expected signature
        hash_digest = hmac.new(
            secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).digest()
        signature = base64.b64encode(hash_digest).decode("utf-8")

        assert verify_webhook_signature(body, signature, secret) is True

    def test_verify_webhook_signature_invalid(self):
        """Test that invalid signatures are rejected."""
        body = b'{"test": "data"}'
        secret = "test_secret"
        invalid_signature = "invalid_signature"

        assert verify_webhook_signature(body, invalid_signature, secret) is False

    def test_verify_webhook_signature_empty_body(self):
        """Test that empty body raises error."""
        with pytest.raises(SignatureVerificationError):
            verify_webhook_signature(b"", "signature", "secret")

    def test_verify_webhook_signature_empty_signature(self):
        """Test that empty signature raises error."""
        with pytest.raises(SignatureVerificationError):
            verify_webhook_signature(b"body", "", "secret")

    def test_verify_webhook_signature_empty_secret(self):
        """Test that empty secret raises error."""
        with pytest.raises(SignatureVerificationError):
            verify_webhook_signature(b"body", "signature", "")

    def test_safe_verify_webhook_signature_none_values(self):
        """Test that safe verification handles None values gracefully."""
        assert safe_verify_webhook_signature(None, None, None) is False
        assert safe_verify_webhook_signature(b"body", None, "secret") is False
        assert safe_verify_webhook_signature(None, "sig", "secret") is False
        assert safe_verify_webhook_signature(b"body", "sig", None) is False


class TestWebhookModels:
    """Test webhook event models."""

    def test_line_text_message_creation(self):
        """Test creating a LINE text message."""
        message = LineTextMessage(
            id="msg123",
            type="text",
            text="Hello, World!",
        )

        assert message.id == "msg123"
        assert message.type == "text"
        assert message.text == "Hello, World!"
        assert message.quoteToken is None
        assert message.quotedMessageId is None

    def test_line_event_source_creation(self):
        """Test creating a LINE event source."""
        source = LineEventSource(
            type="user",
            userId="user123",
        )

        assert source.type == "user"
        assert source.userId == "user123"
        assert source.groupId is None
        assert source.roomId is None

    def test_line_delivery_context_creation(self):
        """Test creating a LINE delivery context."""
        context = LineDeliveryContext(isRedelivery=False)

        assert context.isRedelivery is False

    def test_line_message_event_creation(self):
        """Test creating a complete LINE message event."""
        message = LineTextMessage(
            id="msg123",
            type="text",
            text="Test message",
        )

        source = LineEventSource(
            type="user",
            userId="user123",
        )

        delivery_context = LineDeliveryContext(isRedelivery=False)

        event = LineMessageEvent(
            type="message",
            timestamp=1234567890,
            source=source,
            mode="active",
            webhookEventId="event123",
            deliveryContext=delivery_context,
            replyToken="reply123",
            message=message,
        )

        assert event.type == "message"
        assert event.timestamp == 1234567890
        assert event.source.userId == "user123"
        assert event.mode == "active"
        assert event.webhookEventId == "event123"
        assert event.replyToken == "reply123"
        assert event.message.text == "Test message"

    def test_line_webhook_payload_creation(self):
        """Test creating a complete webhook payload."""
        message = LineTextMessage(
            id="msg123",
            type="text",
            text="Test message",
        )

        source = LineEventSource(
            type="user",
            userId="user123",
        )

        delivery_context = LineDeliveryContext(isRedelivery=False)

        event = LineMessageEvent(
            type="message",
            timestamp=1234567890,
            source=source,
            mode="active",
            webhookEventId="event123",
            deliveryContext=delivery_context,
            replyToken="reply123",
            message=message,
        )

        payload = LineWebhookPayload(
            destination="bot123",
            events=[event],
        )

        assert payload.destination == "bot123"
        assert len(payload.events) == 1
        assert payload.events[0].type == "message"


class TestWebhookHandler:
    """Test webhook handler functionality."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        with patch.dict(
            "os.environ",
            {
                "LINE_CHANNEL_SECRET": "test_secret",
                "LINE_CHANNEL_ACCESS_TOKEN": "test_token",
            },
        ):
            return LineAPIConfig()

    @pytest.fixture
    def handler(self, config):
        """Create test webhook handler."""
        return LineWebhookHandler(config)

    def test_handler_initialization(self, config):
        """Test webhook handler initialization."""
        handler = LineWebhookHandler(config)

        assert handler.config == config
        assert handler.verify_signature is True
        assert handler.track_processed_events is True
        assert len(handler._event_handlers) == 0
        assert len(handler._processed_events) == 0

    def test_handler_initialization_with_options(self, config):
        """Test webhook handler initialization with custom options."""
        handler = LineWebhookHandler(
            config,
            verify_signature=False,
            track_processed_events=False,
        )

        assert handler.verify_signature is False
        assert handler.track_processed_events is False

    def test_register_handler(self, handler):
        """Test registering event handlers."""

        async def test_handler(event):
            pass

        handler.register_handler("message", test_handler)

        assert "message" in handler._event_handlers
        assert len(handler._event_handlers["message"]) == 1

    def test_message_handler_decorator(self, handler):
        """Test message handler decorator."""

        @handler.message_handler
        async def handle_message(event: LineMessageEvent):
            return "handled"

        assert "message" in handler._event_handlers
        assert len(handler._event_handlers["message"]) == 1

    def test_postback_handler_decorator(self, handler):
        """Test postback handler decorator."""

        @handler.postback_handler
        async def handle_postback(event):
            return "handled"

        assert "postback" in handler._event_handlers
        assert len(handler._event_handlers["postback"]) == 1

    def test_get_handler_count(self, handler):
        """Test getting handler count."""

        @handler.message_handler
        async def handle_message(event):
            pass

        @handler.postback_handler
        async def handle_postback(event):
            pass

        counts = handler.get_handler_count()
        assert counts["message"] == 1
        assert counts["postback"] == 1

    @pytest.mark.asyncio
    async def test_handle_webhook_no_signature_verification(self, config):
        """Test handling webhook without signature verification."""
        handler = LineWebhookHandler(config, verify_signature=False)

        payload_dict = {
            "destination": "bot123",
            "events": [],
        }

        response = await handler.handle_webhook(
            request_body=b'{"test": "data"}',
            signature=None,
            payload_dict=payload_dict,
        )

        assert response.status == "OK"
        assert response.processed_events == 0
        assert "No events" in response.message

    @pytest.mark.asyncio
    async def test_handle_webhook_invalid_signature(self, handler):
        """Test handling webhook with invalid signature."""
        payload_dict = {
            "destination": "bot123",
            "events": [],
        }

        response = await handler.handle_webhook(
            request_body=b'{"test": "data"}',
            signature="invalid_signature",
            payload_dict=payload_dict,
        )

        assert response.status == "ERROR"
        assert "Invalid signature" in response.message
        assert response.processed_events == 0

    @pytest.mark.asyncio
    async def test_handle_webhook_invalid_payload(self, config):
        """Test handling webhook with invalid payload."""
        handler = LineWebhookHandler(config, verify_signature=False)

        # Invalid payload missing required fields
        payload_dict = {
            "invalid": "payload",
        }

        response = await handler.handle_webhook(
            request_body=b'{"test": "data"}',
            signature=None,
            payload_dict=payload_dict,
        )

        assert response.status == "ERROR"
        assert "Invalid payload" in response.message
        assert response.processed_events == 0

    @pytest.mark.asyncio
    async def test_handle_webhook_with_events(self, config):
        """Test handling webhook with events."""
        handler = LineWebhookHandler(config, verify_signature=False)

        # Register a test handler
        handled_events = []

        @handler.message_handler
        async def handle_message(event: LineMessageEvent):
            handled_events.append(event)

        # Create test payload
        payload_dict = {
            "destination": "bot123",
            "events": [
                {
                    "type": "message",
                    "timestamp": 1234567890,
                    "source": {
                        "type": "user",
                        "userId": "user123",
                    },
                    "mode": "active",
                    "webhookEventId": "event123",
                    "deliveryContext": {
                        "isRedelivery": False,
                    },
                    "replyToken": "reply123",
                    "message": {
                        "id": "msg123",
                        "type": "text",
                        "text": "Hello!",
                    },
                },
            ],
        }

        response = await handler.handle_webhook(
            request_body=b'{"test": "data"}',
            signature=None,
            payload_dict=payload_dict,
        )

        assert response.status == "OK"
        assert response.processed_events == 1
        assert len(handled_events) == 1
        assert handled_events[0].message.text == "Hello!"

    def test_clear_processed_events(self, handler):
        """Test clearing processed events cache."""
        handler._processed_events.add("event1")
        handler._processed_events.add("event2")

        assert handler.get_processed_event_count() == 2

        handler.clear_processed_events()

        assert handler.get_processed_event_count() == 0
