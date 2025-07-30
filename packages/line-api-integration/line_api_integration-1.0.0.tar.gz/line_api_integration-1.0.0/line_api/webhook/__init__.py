"""
LINE Webhook Module.

This module provides comprehensive webhook handling for LINE Platform events,
including signature verification, event parsing, and structured response handling.

Features:
- Type-safe webhook event models with Pydantic validation
- Signature verification utilities for security
- Flexible event handler system with decorators
- Comprehensive error handling and logging
- Support for all LINE webhook event types

Usage Example:
    ```python
    from line_api.webhook import LineWebhookHandler
    from line_api.core import LineAPIConfig

    # Initialize configuration
    config = LineAPIConfig()

    # Create webhook handler
    handler = LineWebhookHandler(config)

    # Register event handlers using decorators
    @handler.message_handler
    async def handle_message(event: LineMessageEvent) -> None:
        if event.message.type == "text":
            print(f"Received: {event.message.text}")

    @handler.postback_handler
    async def handle_postback(event: LinePostbackEvent) -> None:
        print(f"Postback: {event.postback.data}")

    # In your FastAPI endpoint:
    @app.post("/webhook")
    async def webhook_endpoint(request: Request):
        response = await handler.handle_webhook(
            request_body=await request.body(),
            signature=request.headers.get("X-Line-Signature"),
            payload_dict=await request.json()
        )
        return response.model_dump()
    ```

"""

from .handler import LineWebhookHandler, WebhookHandlerError
from .models import (
    LineAccountLinkEvent,
    LineAudioMessage,
    LineBeaconEvent,
    LineDeliveryContext,
    LineEvent,
    LineEventSource,
    LineFileMessage,
    LineFollowEvent,
    LineImageMessage,
    LineJoinEvent,
    LineLeaveEvent,
    LineLocationMessage,
    LineMemberJoinEvent,
    LineMemberLeaveEvent,
    LineMention,
    LineMentionObject,
    LineMessage,
    LineMessageEvent,
    LinePostback,
    LinePostbackEvent,
    LineStickerMessage,
    LineTextMessage,
    LineUnfollowEvent,
    LineUnsendEvent,
    LineVideoMessage,
    LineVideoPlayCompleteEvent,
    LineWebhookPayload,
    WebhookResponse,
)
from .signature import (
    SignatureVerificationError,
    safe_verify_webhook_signature,
    verify_webhook_signature,
)

__all__ = [
    "LineAccountLinkEvent",
    "LineAudioMessage",
    "LineBeaconEvent",
    "LineDeliveryContext",
    "LineEvent",
    "LineEventSource",
    "LineFileMessage",
    "LineFollowEvent",
    "LineImageMessage",
    "LineJoinEvent",
    "LineLeaveEvent",
    "LineLocationMessage",
    "LineMemberJoinEvent",
    "LineMemberLeaveEvent",
    "LineMention",
    "LineMentionObject",
    "LineMessage",
    "LineMessageEvent",
    "LinePostback",
    "LinePostbackEvent",
    "LineStickerMessage",
    "LineTextMessage",
    "LineUnfollowEvent",
    "LineUnsendEvent",
    "LineVideoMessage",
    "LineVideoPlayCompleteEvent",
    "LineWebhookHandler",
    "LineWebhookPayload",
    "SignatureVerificationError",
    "WebhookHandlerError",
    "WebhookResponse",
    "safe_verify_webhook_signature",
    "verify_webhook_signature",
]
