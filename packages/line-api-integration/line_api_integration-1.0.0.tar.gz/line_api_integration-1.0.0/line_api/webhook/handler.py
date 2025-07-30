"""
LINE Webhook Handler.

This module provides a comprehensive webhook handler for LINE Platform events,
including signature verification, event parsing, and structured response handling.

Based on your example logic and the official LINE Messaging API documentation:
https://developers.line.biz/en/docs/messaging-api/receiving-messages/
"""

import logging
from collections.abc import Callable, Coroutine
from typing import Any, Optional

from line_api.core.config import LineAPIConfig
from line_api.core.exceptions import LineAPIError

from .models import (
    LineEvent,
    LineMessageEvent,
    LinePostbackEvent,
    LineWebhookPayload,
    WebhookResponse,
)
from .signature import safe_verify_webhook_signature

logger = logging.getLogger(__name__)


# Type alias for event handler functions
EventHandlerFunction = Callable[[LineEvent], Coroutine[Any, Any, Any]]


class WebhookHandlerError(LineAPIError):
    """Exception raised when webhook processing fails."""

    pass


class LineWebhookHandler:
    """
    Comprehensive LINE webhook handler with signature verification and event processing.

    This handler provides a type-safe, async-first approach to processing LINE webhooks
    with comprehensive error handling and flexible event routing.

    Features:
    - Automatic signature verification
    - Type-safe event parsing with Pydantic models
    - Flexible event handler registration
    - Comprehensive error handling and logging
    - Support for duplicate event detection
    - Graceful handling of unknown event types

    Example:
        ```python
        from line_api.webhook import LineWebhookHandler
        from line_api.core import LineAPIConfig

        config = LineAPIConfig()
        handler = LineWebhookHandler(config)

        @handler.message_handler
        async def handle_message(event: LineMessageEvent) -> None:
            print(f"Received message: {event.message.text}")

        @handler.postback_handler
        async def handle_postback(event: LinePostbackEvent) -> None:
            print(f"Received postback: {event.postback.data}")

        # In your FastAPI endpoint:
        response = await handler.handle_webhook(
            request_body=await request.body(),
            signature=request.headers.get("X-Line-Signature"),
            payload_dict=await request.json()
        )
        ```

    """

    def __init__(
        self,
        config: LineAPIConfig,
        verify_signature: bool = True,
        track_processed_events: bool = True,
    ) -> None:
        """
        Initialize the webhook handler.

        Args:
            config: LINE API configuration containing channel secret
            verify_signature: Whether to verify webhook signatures (default: True)
            track_processed_events: Whether to track processed events to prevent duplicates

        """
        self.config = config
        self.verify_signature = verify_signature
        self.track_processed_events = track_processed_events

        # Event handlers registry
        self._event_handlers: dict[str, list[EventHandlerFunction]] = {}

        # Processed events tracking for duplicate detection
        self._processed_events: set[str] = set()

        logger.info(
            "WebhookHandler initialized - signature_verification=%s, event_tracking=%s",
            verify_signature,
            track_processed_events,
        )

    def register_handler(
        self,
        event_type: str,
        handler: EventHandlerFunction,
    ) -> None:
        """
        Register an event handler for a specific event type.

        Args:
            event_type: Type of event to handle (e.g., 'message', 'postback')
            handler: Async function to handle the event

        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []

        self._event_handlers[event_type].append(handler)
        logger.debug("Registered handler for event type: %s", event_type)

    def message_handler(
        self,
        func: Callable[[LineMessageEvent], Coroutine[Any, Any, Any]],
    ) -> Callable[[LineMessageEvent], Coroutine[Any, Any, Any]]:
        """
        Decorator to register a message event handler.

        Args:
            func: Async function that handles LineMessageEvent

        Returns:
            The original function (for use as decorator)

        """

        async def wrapper(event: LineEvent) -> Any:
            if isinstance(event, LineMessageEvent):
                return await func(event)

        self.register_handler("message", wrapper)
        return func

    def postback_handler(
        self,
        func: Callable[[LinePostbackEvent], Coroutine[Any, Any, Any]],
    ) -> Callable[[LinePostbackEvent], Coroutine[Any, Any, Any]]:
        """
        Decorator to register a postback event handler.

        Args:
            func: Async function that handles LinePostbackEvent

        Returns:
            The original function (for use as decorator)

        """

        async def wrapper(event: LineEvent) -> Any:
            if isinstance(event, LinePostbackEvent):
                return await func(event)

        self.register_handler("postback", wrapper)
        return func

    def follow_handler(
        self,
        func: Callable[[LineEvent], Coroutine[Any, Any, Any]],
    ) -> Callable[[LineEvent], Coroutine[Any, Any, Any]]:
        """
        Decorator to register a follow event handler.

        Args:
            func: Async function that handles follow events

        Returns:
            The original function (for use as decorator)

        """
        self.register_handler("follow", func)
        return func

    def unfollow_handler(
        self,
        func: Callable[[LineEvent], Coroutine[Any, Any, Any]],
    ) -> Callable[[LineEvent], Coroutine[Any, Any, Any]]:
        """
        Decorator to register an unfollow event handler.

        Args:
            func: Async function that handles unfollow events

        Returns:
            The original function (for use as decorator)

        """
        self.register_handler("unfollow", func)
        return func

    def join_handler(
        self,
        func: Callable[[LineEvent], Coroutine[Any, Any, Any]],
    ) -> Callable[[LineEvent], Coroutine[Any, Any, Any]]:
        """
        Decorator to register a join event handler.

        Args:
            func: Async function that handles join events

        Returns:
            The original function (for use as decorator)

        """
        self.register_handler("join", func)
        return func

    def leave_handler(
        self,
        func: Callable[[LineEvent], Coroutine[Any, Any, Any]],
    ) -> Callable[[LineEvent], Coroutine[Any, Any, Any]]:
        """
        Decorator to register a leave event handler.

        Args:
            func: Async function that handles leave events

        Returns:
            The original function (for use as decorator)

        """
        self.register_handler("leave", func)
        return func

    def unsend_handler(
        self,
        func: Callable[[LineEvent], Coroutine[Any, Any, Any]],
    ) -> Callable[[LineEvent], Coroutine[Any, Any, Any]]:
        """
        Decorator to register an unsend event handler.

        Args:
            func: Async function that handles unsend events

        Returns:
            The original function (for use as decorator)

        """
        self.register_handler("unsend", func)
        return func

    async def _verify_signature(
        self,
        request_body: bytes,
        signature: Optional[str],
    ) -> bool:
        """
        Verify the webhook signature.

        Args:
            request_body: Raw request body as bytes
            signature: X-Line-Signature header value

        Returns:
            True if signature is valid or verification is disabled

        """
        if not self.verify_signature:
            logger.debug("Signature verification disabled")
            return True

        if not self.config.channel_secret:
            logger.error("Channel secret not configured for signature verification")
            return False

        return safe_verify_webhook_signature(
            request_body=request_body,
            signature=signature,
            channel_secret=self.config.channel_secret,
        )

    def _is_duplicate_event(self, event: LineEvent) -> bool:
        """
        Check if an event has already been processed.

        Args:
            event: Event to check

        Returns:
            True if event is a duplicate

        """
        if not self.track_processed_events:
            return False

        event_id = event.webhookEventId
        if event_id in self._processed_events:
            logger.warning("Duplicate event detected: %s", event_id)
            return True

        self._processed_events.add(event_id)
        return False

    async def _process_event(self, event: LineEvent) -> None:
        """
        Process a single webhook event.

        Args:
            event: Event to process

        """
        event_type = event.type
        handlers = self._event_handlers.get(event_type, [])

        if not handlers:
            logger.debug("No handlers registered for event type: %s", event_type)
            return

        logger.debug(
            "Processing event %s (type: %s) with %d handlers",
            event.webhookEventId,
            event_type,
            len(handlers),
        )

        # Execute all registered handlers for this event type
        for handler in handlers:
            try:
                await handler(event)
                logger.debug(
                    "Handler executed successfully for event %s",
                    event.webhookEventId,
                )
            except Exception as e:
                logger.error(
                    "Handler failed for event %s: %s",
                    event.webhookEventId,
                    str(e),
                    exc_info=True,
                )
                # Continue processing other handlers even if one fails

    async def handle_webhook(
        self,
        request_body: bytes,
        signature: Optional[str],
        payload_dict: dict[str, Any],
    ) -> WebhookResponse:
        """
        Handle a complete webhook request.

        Args:
            request_body: Raw request body as bytes
            signature: X-Line-Signature header value
            payload_dict: Parsed JSON payload as dictionary

        Returns:
            WebhookResponse indicating processing status

        Raises:
            WebhookHandlerError: If webhook processing fails critically

        """
        logger.info("Processing webhook request with %d bytes", len(request_body))

        try:
            # Verify signature
            if not await self._verify_signature(request_body, signature):
                logger.warning("Webhook signature verification failed")
                return WebhookResponse(
                    status="ERROR",
                    message="Invalid signature",
                    processed_events=0,
                )

            # Parse payload
            try:
                payload = LineWebhookPayload.model_validate(payload_dict)
            except Exception as e:
                logger.error("Invalid webhook payload: %s", str(e))
                return WebhookResponse(
                    status="ERROR",
                    message=f"Invalid payload: {e}",
                    processed_events=0,
                )

            # Early return if no events
            if not payload.events:
                logger.info("Webhook contains no events")
                return WebhookResponse(
                    status="OK",
                    message="No events to process",
                    processed_events=0,
                )

            processed_count = 0

            # Process each event
            for event in payload.events:
                try:
                    # Skip duplicate events
                    if self._is_duplicate_event(event):
                        continue

                    # Process the event
                    await self._process_event(event)
                    processed_count += 1

                    logger.debug(
                        "Successfully processed event %s (type: %s)",
                        event.webhookEventId,
                        event.type,
                    )

                except Exception as e:
                    logger.error(
                        "Failed to process event %s: %s",
                        getattr(event, "webhookEventId", "unknown"),
                        str(e),
                        exc_info=True,
                    )
                    # Continue processing other events

            logger.info(
                "Webhook processing completed: %d/%d events processed",
                processed_count,
                len(payload.events),
            )

            return WebhookResponse(
                status="OK",
                message=f"Processed {processed_count} events",
                processed_events=processed_count,
            )

        except Exception as e:
            logger.error("Critical error in webhook processing: %s", str(e))
            raise WebhookHandlerError(f"Webhook processing failed: {e}") from e

    def get_handler_count(self) -> dict[str, int]:
        """
        Get the number of registered handlers for each event type.

        Returns:
            Dictionary mapping event type to handler count

        """
        return {
            event_type: len(handlers)
            for event_type, handlers in self._event_handlers.items()
        }

    def clear_processed_events(self) -> None:
        """Clear the processed events cache."""
        self._processed_events.clear()
        logger.debug("Cleared processed events cache")

    def get_processed_event_count(self) -> int:
        """
        Get the number of processed events in cache.

        Returns:
            Number of processed events

        """
        return len(self._processed_events)
