"""
LINE Webhook Integration Example.

This example demonstrates how to integrate LINE webhooks with a FastAPI application,
including proper signature verification, event handling, and response management.

Features demonstrated:
- FastAPI webhook endpoint setup
- Signature verification and security
- Event-specific handlers with decorators
- Error handling and logging
- Integration with LINE Messaging API for responses

Requirements:
    pip install fastapi uvicorn

Usage:
    1. Set up your LINE Bot channel and get credentials
    2. Set environment variables:
       LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
       LINE_CHANNEL_SECRET=your_channel_secret
    3. Run the server: uvicorn webhook_example:app --reload
    4. Set your webhook URL in LINE Developers Console to: https://your-domain/webhook
"""

import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from line_api import (
    LineAPIConfig,
    LineEvent,
    LineMessageEvent,
    LineMessagingClient,
    LinePostbackEvent,
    LineWebhookHandler,
    SignatureVerificationError,
    TextMessage,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LINE Webhook Example",
    description="Example implementation of LINE webhook handling with FastAPI",
    version="1.0.0",
)

# Initialize LINE API components
try:
    config = LineAPIConfig()
    webhook_handler = LineWebhookHandler(config)
    messaging_client = LineMessagingClient(config)
except Exception as e:
    logger.error(f"Failed to initialize LINE API components: {e}")
    logger.error("Make sure LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET are set")
    raise


@webhook_handler.message_handler
async def handle_message_event(event: LineMessageEvent) -> None:
    """Handle incoming message events."""
    logger.info(f"Received message event from user: {event.source.userId}")

    # Handle different message types
    if event.message.type == "text":
        text_message = event.message  # This will be LineTextMessage
        user_text = text_message.text
        logger.info(f"User sent text: {user_text}")

        # Create response based on user input
        if user_text.lower() in ["hello", "hi", "hey"]:
            response_text = "Hello! How can I help you today?"
        elif user_text.lower() in ["bye", "goodbye", "see you"]:
            response_text = "Goodbye! Have a great day!"
        elif user_text.lower() == "help":
            response_text = (
                "Available commands:\n"
                "• hello - Greet the bot\n"
                "• help - Show this help message\n"
                "• status - Check bot status\n"
                "• bye - Say goodbye"
            )
        elif user_text.lower() == "status":
            response_text = "🟢 Bot is running and ready to help!"
        else:
            response_text = f"Thanks for your message: '{user_text}'. Try saying 'help' for available commands."

        # Send reply (only if replyToken is available)
        if event.replyToken:
            await messaging_client.reply_message(
                reply_token=event.replyToken,
                messages=[TextMessage(text=response_text)],
            )

    elif event.message.type == "sticker":
        # Handle sticker messages
        if event.replyToken:
            await messaging_client.reply_message(
                reply_token=event.replyToken,
                messages=[TextMessage(text="Nice sticker! 😊")],
            )

    elif event.message.type == "image":
        # Handle image messages
        if event.replyToken:
            await messaging_client.reply_message(
                reply_token=event.replyToken,
                messages=[TextMessage(text="Thanks for sharing the image! 📸")],
            )

    else:
        # Handle other message types
        if event.replyToken:
            await messaging_client.reply_message(
                reply_token=event.replyToken,
                messages=[
                    TextMessage(
                        text=f"Received a {event.message.type} message. Thanks for sharing!",
                    ),
                ],
            )


@webhook_handler.postback_handler
async def handle_postback_event(event: LinePostbackEvent) -> None:
    """Handle postback events from interactive elements."""
    logger.info(f"Received postback event from user: {event.source.userId}")

    postback_data = event.postback.data
    logger.info(f"Postback data: {postback_data}")

    # Handle different postback actions
    if postback_data == "action=menu":
        response_text = "Main menu selected! What would you like to do?"
    elif postback_data.startswith("action=select_"):
        item = postback_data.replace("action=select_", "")
        response_text = f"You selected: {item}"
    else:
        response_text = f"Postback received: {postback_data}"

    if event.replyToken:
        await messaging_client.reply_message(
            reply_token=event.replyToken,
            messages=[TextMessage(text=response_text)],
        )


@webhook_handler.follow_handler
async def handle_follow_event(event: LineEvent) -> None:
    """Handle follow events when users add the bot as a friend."""
    logger.info(
        f"New user followed the bot: {getattr(event.source, 'userId', 'unknown')}",
    )

    welcome_message = (
        "🎉 Welcome! Thanks for adding me as a friend!\n\n"
        "I'm here to help you. Try saying 'help' to see what I can do."
    )

    reply_token = getattr(event, "replyToken", None)
    if reply_token:
        await messaging_client.reply_message(
            reply_token=reply_token,
            messages=[TextMessage(text=welcome_message)],
        )


@webhook_handler.unfollow_handler
async def handle_unfollow_event(event: LineEvent) -> None:
    """Handle unfollow events when users remove the bot."""
    logger.info(
        f"User unfollowed the bot: {getattr(event.source, 'userId', 'unknown')}",
    )
    # Note: Cannot send messages to users who unfollowed


@webhook_handler.join_handler
async def handle_join_event(event: LineEvent) -> None:
    """Handle join events when bot is added to a group or room."""
    group_id = getattr(event.source, "groupId", None) or getattr(
        event.source,
        "roomId",
        None,
    )
    logger.info(f"Bot joined group/room: {group_id}")

    greeting_message = (
        "Hello everyone! 👋\n"
        "Thanks for adding me to this group. "
        "Say 'help' to see what I can do!"
    )

    reply_token = getattr(event, "replyToken", None)
    if reply_token:
        await messaging_client.reply_message(
            reply_token=reply_token,
            messages=[TextMessage(text=greeting_message)],
        )


@webhook_handler.leave_handler
async def handle_leave_event(event: LineEvent) -> None:
    """Handle leave events when bot is removed from a group or room."""
    group_id = getattr(event.source, "groupId", None) or getattr(
        event.source,
        "roomId",
        None,
    )
    logger.info(f"Bot left group/room: {group_id}")
    # Note: Cannot send messages after leaving


@app.get("/")
async def root() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "LINE Webhook Server is running", "version": "1.0.0"}


@app.post("/")
async def root_webhook(request: Request) -> JSONResponse:
    """
    Alternative webhook endpoint at root path.

    Some LINE configurations send webhooks to root instead of /webhook.
    This endpoint redirects to the main webhook handler.
    """
    logger.info("Webhook received at root path, processing...")
    return await webhook_endpoint(request)


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "service": "LINE Webhook Handler",
        "webhook_handler": "ready",
        "messaging_client": "ready",
    }


@app.post("/webhook")
async def webhook_endpoint(request: Request) -> JSONResponse:
    """
    Main webhook endpoint for receiving LINE Platform events.

    This endpoint:
    1. Receives webhook requests from LINE Platform
    2. Verifies the signature for security
    3. Parses events and delegates to appropriate handlers
    4. Returns proper response to LINE Platform
    """
    try:
        # Get request data
        body = await request.body()
        signature = request.headers.get("X-Line-Signature")

        if not signature:
            logger.error("Missing X-Line-Signature header")
            raise HTTPException(status_code=400, detail="Missing signature header")

        # Parse JSON payload
        try:
            payload_dict = await request.json()
        except Exception as e:
            logger.error(f"Failed to parse JSON payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        # Process webhook with handler
        response = await webhook_handler.handle_webhook(
            request_body=body,
            signature=signature,
            payload_dict=payload_dict,
        )

        logger.info(
            f"Successfully processed webhook with {response.processed_events} events",
        )

        # Return success response
        return JSONResponse(
            status_code=200,
            content=response.model_dump(),
        )

    except SignatureVerificationError as e:
        logger.error(f"Signature verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid signature")

    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting LINE Webhook server...")
    logger.info(
        "Make sure to set LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET environment variables",
    )

    uvicorn.run(
        "webhook_example:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info",
    )
