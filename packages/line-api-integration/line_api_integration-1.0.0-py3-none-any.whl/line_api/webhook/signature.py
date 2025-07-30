"""
LINE Webhook Signature Verification.

This module provides utilities for verifying LINE webhook signatures
to ensure the authenticity and integrity of webhook requests.

Based on the official LINE Messaging API documentation:
https://developers.line.biz/en/docs/messaging-api/verify-webhook-signature/
"""

import base64
import hashlib
import hmac
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SignatureVerificationError(Exception):
    """Exception raised when webhook signature verification fails."""

    pass


def verify_webhook_signature(
    request_body: bytes,
    signature: str,
    channel_secret: str,
) -> bool:
    """
    Verify the signature of a LINE webhook request.

    Args:
        request_body: Raw request body as bytes
        signature: X-Line-Signature header value
        channel_secret: LINE channel secret

    Returns:
        True if signature is valid, False otherwise

    Raises:
        SignatureVerificationError: If verification parameters are invalid

    """
    if not request_body:
        raise SignatureVerificationError("Request body cannot be empty")

    if not signature:
        raise SignatureVerificationError("Signature cannot be empty")

    if not channel_secret:
        raise SignatureVerificationError("Channel secret cannot be empty")

    try:
        # Create HMAC-SHA256 hash
        hash_digest = hmac.new(
            channel_secret.encode("utf-8"),
            request_body,
            hashlib.sha256,
        ).digest()

        # Encode to base64
        expected_signature = base64.b64encode(hash_digest).decode("utf-8")

        # Compare signatures
        is_valid = hmac.compare_digest(signature, expected_signature)

        if not is_valid:
            logger.warning(
                "Webhook signature verification failed. Expected: %s, Received: %s",
                expected_signature[:10] + "...",
                signature[:10] + "...",
            )

        return is_valid

    except Exception as e:
        logger.error("Error during signature verification: %s", str(e))
        raise SignatureVerificationError(f"Signature verification failed: {e}")


def safe_verify_webhook_signature(
    request_body: Optional[bytes],
    signature: Optional[str],
    channel_secret: Optional[str],
) -> bool:
    """
    Safely verify webhook signature with comprehensive error handling.

    This function provides a safe wrapper around verify_webhook_signature
    that handles None values and catches all exceptions.

    Args:
        request_body: Raw request body as bytes (can be None)
        signature: X-Line-Signature header value (can be None)
        channel_secret: LINE channel secret (can be None)

    Returns:
        True if signature is valid, False for any error or invalid signature

    """
    try:
        if not all([request_body, signature, channel_secret]):
            logger.warning(
                "Webhook signature verification failed: missing required parameters",
            )
            return False

        # Type assertion after None check
        assert request_body is not None
        assert signature is not None
        assert channel_secret is not None

        return verify_webhook_signature(request_body, signature, channel_secret)

    except Exception as e:
        logger.error("Safe signature verification failed: %s", str(e))
        return False
