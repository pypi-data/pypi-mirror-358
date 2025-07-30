"""
LineKit - LINE API Integration Library.

A comprehensive, type-safe Python library for integrating with LINE's APIs.
"""

from .core import LineAPIConfig
from .flex_messages import (
    FlexBox,
    FlexBubble,
    FlexButton,
    FlexCarousel,
    FlexImage,
    FlexLayout,
    FlexMessage,
    FlexSeparator,
    FlexText,
    export_flex_json,
    print_flex_json,
    validate_flex_json,
)
from .messaging import LineMessagingClient, TextMessage
from .webhook import (
    LineEvent,
    LineMessageEvent,
    LinePostbackEvent,
    LineWebhookHandler,
    SignatureVerificationError,
    verify_webhook_signature,
)

__version__ = "1.0.1"

__all__ = [
    "FlexBox",
    "FlexBubble",
    "FlexButton",
    "FlexCarousel",
    "FlexImage",
    "FlexLayout",
    "FlexMessage",
    "FlexSeparator",
    "FlexText",
    "LineAPIConfig",
    "LineEvent",
    "LineMessageEvent",
    "LineMessagingClient",
    "LinePostbackEvent",
    "LineWebhookHandler",
    "SignatureVerificationError",
    "TextMessage",
    "export_flex_json",
    "print_flex_json",
    "validate_flex_json",
    "verify_webhook_signature",
]
