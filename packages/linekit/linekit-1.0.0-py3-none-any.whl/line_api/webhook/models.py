"""
LINE Webhook Models

This module provides Pydantic models for LINE webhook events and payloads,
ensuring type safety and validation for all webhook data structures.

Based on the official LINE Messaging API documentation:
https://developers.line.biz/en/reference/messaging-api/#webhook-event-objects
"""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class LineDeliveryContext(BaseModel):
    """
    Delivery context for webhook events.

    Attributes:
        isRedelivery: Whether this is a redelivered webhook

    """

    isRedelivery: bool = Field(
        description="Whether this webhook is being redelivered",
    )


class LineMention(BaseModel):
    """
    Mention information in text messages.

    Attributes:
        index: Start position of mention in text
        length: Length of mention text
        userId: User ID of mentioned user
        type: Type of mention (always 'user')
        isSelf: Whether the mention refers to the bot itself

    """

    index: int = Field(description="Start position of mention in text")
    length: int = Field(description="Length of mention text")
    userId: str = Field(description="User ID of mentioned user")
    type: Literal["user"] = Field(description="Type of mention")
    isSelf: Optional[bool] = Field(
        default=None,
        description="Whether mention refers to the bot",
    )


class LineMentionObject(BaseModel):
    """
    Container for mention information.

    Attributes:
        mentionees: List of mentioned users

    """

    mentionees: List[LineMention] = Field(description="List of mentioned users")


class LineTextMessage(BaseModel):
    """
    Text message from webhook.

    Attributes:
        id: Message ID
        type: Message type
        text: Message text content
        quoteToken: Token for quoting this message
        quotedMessageId: ID of quoted message (if this is a quote reply)
        mention: Mention information if text contains mentions
        emojis: Emoji information (if any)

    """

    id: str = Field(description="Unique message ID")
    type: Literal["text"] = Field(description="Message type")
    text: str = Field(description="Text content of the message")
    quoteToken: Optional[str] = Field(
        default=None,
        description="Token for quoting this message",
    )
    quotedMessageId: Optional[str] = Field(
        default=None,
        description="ID of quoted message",
    )
    mention: Optional[LineMentionObject] = Field(
        default=None,
        description="Mention information",
    )
    emojis: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Emoji information",
    )


class LineImageMessage(BaseModel):
    """
    Image message from webhook.

    Attributes:
        id: Message ID
        type: Message type
        quoteToken: Token for quoting this message
        quotedMessageId: ID of quoted message (if this is a quote reply)
        contentProvider: Content provider information
        imageSet: Image set information (if part of image set)

    """

    id: str = Field(description="Unique message ID")
    type: Literal["image"] = Field(description="Message type")
    quoteToken: Optional[str] = Field(
        default=None,
        description="Token for quoting this message",
    )
    quotedMessageId: Optional[str] = Field(
        default=None,
        description="ID of quoted message",
    )
    contentProvider: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Content provider information",
    )
    imageSet: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Image set information",
    )


class LineVideoMessage(BaseModel):
    """
    Video message from webhook.

    Attributes:
        id: Message ID
        type: Message type
        quoteToken: Token for quoting this message
        quotedMessageId: ID of quoted message (if this is a quote reply)
        duration: Video duration in milliseconds
        contentProvider: Content provider information

    """

    id: str = Field(description="Unique message ID")
    type: Literal["video"] = Field(description="Message type")
    quoteToken: Optional[str] = Field(
        default=None,
        description="Token for quoting this message",
    )
    quotedMessageId: Optional[str] = Field(
        default=None,
        description="ID of quoted message",
    )
    duration: Optional[int] = Field(
        default=None,
        description="Video duration in milliseconds",
    )
    contentProvider: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Content provider information",
    )


class LineAudioMessage(BaseModel):
    """
    Audio message from webhook.

    Attributes:
        id: Message ID
        type: Message type
        quoteToken: Token for quoting this message
        quotedMessageId: ID of quoted message (if this is a quote reply)
        duration: Audio duration in milliseconds
        contentProvider: Content provider information

    """

    id: str = Field(description="Unique message ID")
    type: Literal["audio"] = Field(description="Message type")
    quoteToken: Optional[str] = Field(
        default=None,
        description="Token for quoting this message",
    )
    quotedMessageId: Optional[str] = Field(
        default=None,
        description="ID of quoted message",
    )
    duration: Optional[int] = Field(
        default=None,
        description="Audio duration in milliseconds",
    )
    contentProvider: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Content provider information",
    )


class LineFileMessage(BaseModel):
    """
    File message from webhook.

    Attributes:
        id: Message ID
        type: Message type
        quoteToken: Token for quoting this message
        quotedMessageId: ID of quoted message (if this is a quote reply)
        fileName: Name of the file
        fileSize: Size of the file in bytes

    """

    id: str = Field(description="Unique message ID")
    type: Literal["file"] = Field(description="Message type")
    quoteToken: Optional[str] = Field(
        default=None,
        description="Token for quoting this message",
    )
    quotedMessageId: Optional[str] = Field(
        default=None,
        description="ID of quoted message",
    )
    fileName: str = Field(description="Name of the uploaded file")
    fileSize: int = Field(description="Size of file in bytes")


class LineStickerMessage(BaseModel):
    """
    Sticker message from webhook.

    Attributes:
        id: Message ID
        type: Message type
        quoteToken: Token for quoting this message
        quotedMessageId: ID of quoted message (if this is a quote reply)
        packageId: Sticker package ID
        stickerId: Sticker ID
        stickerResourceType: Type of sticker resource
        keywords: Keywords associated with sticker
        text: Text representation of sticker (if available)

    """

    id: str = Field(description="Unique message ID")
    type: Literal["sticker"] = Field(description="Message type")
    quoteToken: Optional[str] = Field(
        default=None,
        description="Token for quoting this message",
    )
    quotedMessageId: Optional[str] = Field(
        default=None,
        description="ID of quoted message",
    )
    packageId: str = Field(description="Sticker package ID")
    stickerId: str = Field(description="Sticker ID")
    stickerResourceType: Optional[str] = Field(
        default=None,
        description="Type of sticker resource",
    )
    keywords: Optional[List[str]] = Field(
        default=None,
        description="Keywords associated with sticker",
    )
    text: Optional[str] = Field(
        default=None,
        description="Text representation of sticker",
    )


class LineLocationMessage(BaseModel):
    """
    Location message from webhook.

    Attributes:
        id: Message ID
        type: Message type
        quoteToken: Token for quoting this message
        quotedMessageId: ID of quoted message (if this is a quote reply)
        title: Location title
        address: Location address
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    """

    id: str = Field(description="Unique message ID")
    type: Literal["location"] = Field(description="Message type")
    quoteToken: Optional[str] = Field(
        default=None,
        description="Token for quoting this message",
    )
    quotedMessageId: Optional[str] = Field(
        default=None,
        description="ID of quoted message",
    )
    title: str = Field(description="Location title")
    address: str = Field(description="Location address")
    latitude: float = Field(description="Latitude coordinate")
    longitude: float = Field(description="Longitude coordinate")


# Union type for all message types
LineMessage = Union[
    LineTextMessage,
    LineImageMessage,
    LineVideoMessage,
    LineAudioMessage,
    LineFileMessage,
    LineStickerMessage,
    LineLocationMessage,
]


class LinePostback(BaseModel):
    """
    Postback data from postback events.

    Attributes:
        data: Postback data string
        params: Additional parameters (datetime picker, rich menu switch, etc.)

    """

    data: str = Field(description="Postback data string")
    params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional postback parameters",
    )


class LineEventSource(BaseModel):
    """
    Source information for webhook events.

    Attributes:
        type: Source type (user, group, room)
        userId: User ID (for user and group/room sources)
        groupId: Group ID (for group sources)
        roomId: Room ID (for room sources)

    """

    type: Literal["user", "group", "room"] = Field(description="Source type")
    userId: Optional[str] = Field(default=None, description="User ID")
    groupId: Optional[str] = Field(default=None, description="Group ID")
    roomId: Optional[str] = Field(default=None, description="Room ID")


class LineMessageEvent(BaseModel):
    """
    Message event from webhook.

    Attributes:
        type: Event type
        timestamp: Event timestamp in milliseconds
        source: Event source information
        mode: Channel mode (active or standby)
        webhookEventId: Unique webhook event ID
        deliveryContext: Delivery context information
        replyToken: Reply token for responding to this event
        message: Message object containing the sent message

    """

    type: Literal["message"] = Field(description="Event type")
    timestamp: int = Field(description="Event timestamp in milliseconds")
    source: LineEventSource = Field(description="Event source information")
    mode: Literal["active", "standby"] = Field(description="Channel mode")
    webhookEventId: str = Field(description="Unique webhook event ID")
    deliveryContext: LineDeliveryContext = Field(
        description="Delivery context information",
    )
    replyToken: Optional[str] = Field(
        default=None,
        description="Reply token for responding to this event",
    )
    message: LineMessage = Field(description="Message object")


class LinePostbackEvent(BaseModel):
    """
    Postback event from webhook.

    Attributes:
        type: Event type
        timestamp: Event timestamp in milliseconds
        source: Event source information
        mode: Channel mode (active or standby)
        webhookEventId: Unique webhook event ID
        deliveryContext: Delivery context information
        replyToken: Reply token for responding to this event
        postback: Postback data object

    """

    type: Literal["postback"] = Field(description="Event type")
    timestamp: int = Field(description="Event timestamp in milliseconds")
    source: LineEventSource = Field(description="Event source information")
    mode: Literal["active", "standby"] = Field(description="Channel mode")
    webhookEventId: str = Field(description="Unique webhook event ID")
    deliveryContext: LineDeliveryContext = Field(
        description="Delivery context information",
    )
    replyToken: Optional[str] = Field(
        default=None,
        description="Reply token for responding to this event",
    )
    postback: LinePostback = Field(description="Postback data")


class LineFollowEvent(BaseModel):
    """
    Follow event from webhook (user follows the bot).

    Attributes:
        type: Event type
        timestamp: Event timestamp in milliseconds
        source: Event source information
        mode: Channel mode (active or standby)
        webhookEventId: Unique webhook event ID
        deliveryContext: Delivery context information
        replyToken: Reply token for responding to this event

    """

    type: Literal["follow"] = Field(description="Event type")
    timestamp: int = Field(description="Event timestamp in milliseconds")
    source: LineEventSource = Field(description="Event source information")
    mode: Literal["active", "standby"] = Field(description="Channel mode")
    webhookEventId: str = Field(description="Unique webhook event ID")
    deliveryContext: LineDeliveryContext = Field(
        description="Delivery context information",
    )
    replyToken: Optional[str] = Field(
        default=None,
        description="Reply token for responding to this event",
    )


class LineUnfollowEvent(BaseModel):
    """
    Unfollow event from webhook (user unfollows the bot).

    Attributes:
        type: Event type
        timestamp: Event timestamp in milliseconds
        source: Event source information
        mode: Channel mode (active or standby)
        webhookEventId: Unique webhook event ID
        deliveryContext: Delivery context information

    """

    type: Literal["unfollow"] = Field(description="Event type")
    timestamp: int = Field(description="Event timestamp in milliseconds")
    source: LineEventSource = Field(description="Event source information")
    mode: Literal["active", "standby"] = Field(description="Channel mode")
    webhookEventId: str = Field(description="Unique webhook event ID")
    deliveryContext: LineDeliveryContext = Field(
        description="Delivery context information",
    )


class LineJoinEvent(BaseModel):
    """
    Join event from webhook (bot joins a group/room).

    Attributes:
        type: Event type
        timestamp: Event timestamp in milliseconds
        source: Event source information
        mode: Channel mode (active or standby)
        webhookEventId: Unique webhook event ID
        deliveryContext: Delivery context information
        replyToken: Reply token for responding to this event

    """

    type: Literal["join"] = Field(description="Event type")
    timestamp: int = Field(description="Event timestamp in milliseconds")
    source: LineEventSource = Field(description="Event source information")
    mode: Literal["active", "standby"] = Field(description="Channel mode")
    webhookEventId: str = Field(description="Unique webhook event ID")
    deliveryContext: LineDeliveryContext = Field(
        description="Delivery context information",
    )
    replyToken: Optional[str] = Field(
        default=None,
        description="Reply token for responding to this event",
    )


class LineLeaveEvent(BaseModel):
    """
    Leave event from webhook (bot leaves a group/room).

    Attributes:
        type: Event type
        timestamp: Event timestamp in milliseconds
        source: Event source information
        mode: Channel mode (active or standby)
        webhookEventId: Unique webhook event ID
        deliveryContext: Delivery context information

    """

    type: Literal["leave"] = Field(description="Event type")
    timestamp: int = Field(description="Event timestamp in milliseconds")
    source: LineEventSource = Field(description="Event source information")
    mode: Literal["active", "standby"] = Field(description="Channel mode")
    webhookEventId: str = Field(description="Unique webhook event ID")
    deliveryContext: LineDeliveryContext = Field(
        description="Delivery context information",
    )


class LineMemberJoinEvent(BaseModel):
    """
    Member join event from webhook (user joins a group/room).

    Attributes:
        type: Event type
        timestamp: Event timestamp in milliseconds
        source: Event source information
        mode: Channel mode (active or standby)
        webhookEventId: Unique webhook event ID
        deliveryContext: Delivery context information
        replyToken: Reply token for responding to this event
        joined: Information about joined members

    """

    type: Literal["memberJoined"] = Field(description="Event type")
    timestamp: int = Field(description="Event timestamp in milliseconds")
    source: LineEventSource = Field(description="Event source information")
    mode: Literal["active", "standby"] = Field(description="Channel mode")
    webhookEventId: str = Field(description="Unique webhook event ID")
    deliveryContext: LineDeliveryContext = Field(
        description="Delivery context information",
    )
    replyToken: Optional[str] = Field(
        default=None,
        description="Reply token for responding to this event",
    )
    joined: Dict[str, Any] = Field(description="Information about joined members")


class LineMemberLeaveEvent(BaseModel):
    """
    Member leave event from webhook (user leaves a group/room).

    Attributes:
        type: Event type
        timestamp: Event timestamp in milliseconds
        source: Event source information
        mode: Channel mode (active or standby)
        webhookEventId: Unique webhook event ID
        deliveryContext: Delivery context information
        left: Information about left members

    """

    type: Literal["memberLeft"] = Field(description="Event type")
    timestamp: int = Field(description="Event timestamp in milliseconds")
    source: LineEventSource = Field(description="Event source information")
    mode: Literal["active", "standby"] = Field(description="Channel mode")
    webhookEventId: str = Field(description="Unique webhook event ID")
    deliveryContext: LineDeliveryContext = Field(
        description="Delivery context information",
    )
    left: Dict[str, Any] = Field(description="Information about left members")


class LineUnsendEvent(BaseModel):
    """
    Unsend event from webhook (user unsends a message).

    Attributes:
        type: Event type
        timestamp: Event timestamp in milliseconds
        source: Event source information
        mode: Channel mode (active or standby)
        webhookEventId: Unique webhook event ID
        deliveryContext: Delivery context information
        unsend: Information about the unsent message

    """

    type: Literal["unsend"] = Field(description="Event type")
    timestamp: int = Field(description="Event timestamp in milliseconds")
    source: LineEventSource = Field(description="Event source information")
    mode: Literal["active", "standby"] = Field(description="Channel mode")
    webhookEventId: str = Field(description="Unique webhook event ID")
    deliveryContext: LineDeliveryContext = Field(
        description="Delivery context information",
    )
    unsend: Dict[str, str] = Field(description="Information about unsent message")


class LineVideoPlayCompleteEvent(BaseModel):
    """
    Video play complete event from webhook.

    Attributes:
        type: Event type
        timestamp: Event timestamp in milliseconds
        source: Event source information
        mode: Channel mode (active or standby)
        webhookEventId: Unique webhook event ID
        deliveryContext: Delivery context information
        replyToken: Reply token for responding to this event
        videoPlayComplete: Video play completion information

    """

    type: Literal["videoPlayComplete"] = Field(description="Event type")
    timestamp: int = Field(description="Event timestamp in milliseconds")
    source: LineEventSource = Field(description="Event source information")
    mode: Literal["active", "standby"] = Field(description="Channel mode")
    webhookEventId: str = Field(description="Unique webhook event ID")
    deliveryContext: LineDeliveryContext = Field(
        description="Delivery context information",
    )
    replyToken: Optional[str] = Field(
        default=None,
        description="Reply token for responding to this event",
    )
    videoPlayComplete: Dict[str, Any] = Field(
        description="Video play completion information",
    )


class LineBeaconEvent(BaseModel):
    """
    Beacon event from webhook.

    Attributes:
        type: Event type
        timestamp: Event timestamp in milliseconds
        source: Event source information
        mode: Channel mode (active or standby)
        webhookEventId: Unique webhook event ID
        deliveryContext: Delivery context information
        replyToken: Reply token for responding to this event
        beacon: Beacon information

    """

    type: Literal["beacon"] = Field(description="Event type")
    timestamp: int = Field(description="Event timestamp in milliseconds")
    source: LineEventSource = Field(description="Event source information")
    mode: Literal["active", "standby"] = Field(description="Channel mode")
    webhookEventId: str = Field(description="Unique webhook event ID")
    deliveryContext: LineDeliveryContext = Field(
        description="Delivery context information",
    )
    replyToken: Optional[str] = Field(
        default=None,
        description="Reply token for responding to this event",
    )
    beacon: Dict[str, Any] = Field(description="Beacon information")


class LineAccountLinkEvent(BaseModel):
    """
    Account link event from webhook.

    Attributes:
        type: Event type
        timestamp: Event timestamp in milliseconds
        source: Event source information
        mode: Channel mode (active or standby)
        webhookEventId: Unique webhook event ID
        deliveryContext: Delivery context information
        replyToken: Reply token for responding to this event
        link: Account link information

    """

    type: Literal["accountLink"] = Field(description="Event type")
    timestamp: int = Field(description="Event timestamp in milliseconds")
    source: LineEventSource = Field(description="Event source information")
    mode: Literal["active", "standby"] = Field(description="Channel mode")
    webhookEventId: str = Field(description="Unique webhook event ID")
    deliveryContext: LineDeliveryContext = Field(
        description="Delivery context information",
    )
    replyToken: Optional[str] = Field(
        default=None,
        description="Reply token for responding to this event",
    )
    link: Dict[str, Any] = Field(description="Account link information")


# Union type for all event types
LineEvent = Union[
    LineMessageEvent,
    LinePostbackEvent,
    LineFollowEvent,
    LineUnfollowEvent,
    LineJoinEvent,
    LineLeaveEvent,
    LineMemberJoinEvent,
    LineMemberLeaveEvent,
    LineUnsendEvent,
    LineVideoPlayCompleteEvent,
    LineBeaconEvent,
    LineAccountLinkEvent,
]


class LineWebhookPayload(BaseModel):
    """
    Complete webhook payload from LINE Platform.

    Attributes:
        destination: Bot user ID that should receive the webhook
        events: List of webhook events

    """

    destination: str = Field(description="Bot user ID receiving the webhook")
    events: List[LineEvent] = Field(description="List of webhook events")


class WebhookResponse(BaseModel):
    """
    Standard response for webhook endpoints.

    Attributes:
        status: Response status
        message: Optional response message
        processed_events: Number of events processed

    """

    status: Literal["OK", "ERROR"] = Field(description="Response status")
    message: Optional[str] = Field(default=None, description="Response message")
    processed_events: int = Field(default=0, description="Number of events processed")
