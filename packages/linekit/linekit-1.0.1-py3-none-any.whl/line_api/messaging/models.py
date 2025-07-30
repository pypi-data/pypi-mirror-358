"""LINE messaging models and data structures."""

from __future__ import annotations

from enum import Enum
from typing import Any, Union

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Supported LINE message types."""

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    LOCATION = "location"
    STICKER = "sticker"
    FLEX = "flex"
    TEMPLATE = "template"


class TextMessage(BaseModel):
    """LINE text message."""

    type: str = Field(default="text", description="Message type")
    text: str = Field(..., max_length=5000, description="Message text")

    model_config = {"extra": "forbid"}

    @classmethod
    def create(cls, text: str) -> TextMessage:
        """
        Create a text message.

        Args:
            text: Message text (max 5000 characters)

        Returns:
            TextMessage instance

        """
        return cls(text=text)


class ImageMessage(BaseModel):
    """LINE image message."""

    type: str = Field(default="image", description="Message type")
    originalContentUrl: str = Field(..., description="URL of the original image")
    previewImageUrl: str = Field(..., description="URL of the preview image")

    model_config = {"extra": "forbid"}

    @classmethod
    def create(
        cls,
        original_content_url: str,
        preview_image_url: str | None = None,
    ) -> ImageMessage:
        """
        Create an image message.

        Args:
            original_content_url: URL of the original image
            preview_image_url: URL of the preview image (defaults to original)

        Returns:
            ImageMessage instance

        """
        return cls(
            originalContentUrl=original_content_url,
            previewImageUrl=preview_image_url or original_content_url,
        )


class LocationMessage(BaseModel):
    """LINE location message."""

    type: str = Field(default="location", description="Message type")
    title: str = Field(..., description="Location title")
    address: str = Field(..., description="Location address")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")

    model_config = {"extra": "forbid"}

    @classmethod
    def create(
        cls,
        title: str,
        address: str,
        latitude: float,
        longitude: float,
    ) -> LocationMessage:
        """
        Create a location message.

        Args:
            title: Location title
            address: Location address
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            LocationMessage instance

        """
        return cls(
            title=title,
            address=address,
            latitude=latitude,
            longitude=longitude,
        )


class StickerMessage(BaseModel):
    """LINE sticker message."""

    type: str = Field(default="sticker", description="Message type")
    packageId: str = Field(..., description="Sticker package ID")
    stickerId: str = Field(..., description="Sticker ID")

    model_config = {"extra": "forbid"}

    @classmethod
    def create(cls, package_id: str, sticker_id: str) -> StickerMessage:
        """
        Create a sticker message.

        Args:
            package_id: Sticker package ID
            sticker_id: Sticker ID

        Returns:
            StickerMessage instance

        """
        return cls(packageId=package_id, stickerId=sticker_id)


class FlexMessage(BaseModel):
    """LINE Flex message."""

    type: str = Field(default="flex", description="Message type")
    altText: str = Field(..., description="Alternative text for notifications")
    contents: dict[str, Any] = Field(..., description="Flex message content")

    model_config = {"extra": "forbid"}

    @classmethod
    def create(cls, alt_text: str, contents: dict[str, Any]) -> FlexMessage:
        """
        Create a Flex message.

        Args:
            alt_text: Alternative text for notifications
            contents: Flex message content

        Returns:
            FlexMessage instance

        """
        return cls(altText=alt_text, contents=contents)


# Type alias for all supported message types
AnyMessage = Union[
    TextMessage,
    ImageMessage,
    LocationMessage,
    StickerMessage,
    FlexMessage,
]


class PushMessageRequest(BaseModel):
    """Request model for push message API."""

    to: str = Field(..., description="User ID, group ID, or room ID")
    messages: list[AnyMessage] = Field(
        ...,
        max_length=5,
        description="List of message objects (max 5)",
    )

    model_config = {"extra": "forbid"}


class MulticastMessageRequest(BaseModel):
    """Request model for multicast message API."""

    to: list[str] = Field(
        ...,
        max_length=500,
        description="List of user IDs (max 500)",
    )
    messages: list[AnyMessage] = Field(
        ...,
        max_length=5,
        description="List of message objects (max 5)",
    )

    model_config = {"extra": "forbid"}


class ReplyMessageRequest(BaseModel):
    """Request model for reply message API."""

    # Using camelCase to match LINE API specification
    replyToken: str = Field(..., description="Reply token from webhook event")  # noqa: N815
    messages: list[AnyMessage] = Field(
        ...,
        max_length=5,
        description="List of message objects (max 5)",
    )

    model_config = {"extra": "forbid"}
