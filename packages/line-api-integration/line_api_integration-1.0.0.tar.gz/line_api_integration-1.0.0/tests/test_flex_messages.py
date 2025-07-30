"""Test flex messages functionality."""

import pytest
from pydantic import ValidationError

from line_api.flex_messages import (
    FlexBox,
    FlexBubble,
    FlexLayout,
    FlexMessage,
    FlexText,
    print_flex_json,
)


def test_flex_text_creation() -> None:
    """Test creating a simple FlexText component."""
    text = FlexText.create("Hello, World!")
    assert text.text == "Hello, World!"
    assert text.type == "text"


def test_flex_box_creation() -> None:
    """Test creating a FlexBox with contents."""
    text1 = FlexText.create("First text")
    text2 = FlexText.create("Second text")

    box = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[text1, text2],
        spacing="md",
    )

    assert box.layout == FlexLayout.VERTICAL
    assert len(box.contents) == 2
    assert box.spacing == "md"


def test_flex_bubble_creation() -> None:
    """Test creating a complete FlexBubble."""
    # Create body content
    title = FlexText.create("Sample Title", weight="bold", size="xl")
    message = FlexText.create("This is a sample message", wrap=True)

    body = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[title, message],
        spacing="md",
        padding_all="20px",
    )

    # Create bubble
    bubble = FlexBubble.create(body=body)

    assert bubble.type == "bubble"
    assert bubble.body is not None
    assert len(bubble.body.contents) == 2


def test_flex_message_creation() -> None:
    """Test creating a complete FlexMessage."""
    # Create a simple bubble
    text = FlexText.create("Hello from Flex Message!")
    body = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[text],
        padding_all="20px",
    )
    bubble = FlexBubble.create(body=body)

    # Create flex message
    flex_message = FlexMessage.create(
        alt_text="Hello Flex Message",
        contents=bubble,
    )

    assert flex_message.type == "flex"
    assert flex_message.alt_text == "Hello Flex Message"
    assert isinstance(flex_message.contents, FlexBubble)


def test_flex_message_json_export() -> None:
    """Test exporting flex message as JSON."""
    # Create a simple flex message
    text = FlexText.create("Test Message")
    body = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[text],
    )
    bubble = FlexBubble.create(body=body)

    # Test JSON printing (should not fail)
    result = print_flex_json(bubble, copy_to_clipboard=False)
    assert result is True


def test_pydantic_model_validation() -> None:
    """Test that Pydantic validation works correctly."""
    # Test that invalid enum value raises validation error
    with pytest.raises(ValidationError):
        FlexBox.create(
            layout="invalid_layout",  # type: ignore[arg-type]
            contents=[],
        )


if __name__ == "__main__":
    # Run a simple test
    test_flex_text_creation()
    test_flex_box_creation()
    test_flex_bubble_creation()
    test_flex_message_creation()
    test_flex_message_json_export()
    print("✅ All flex message tests passed!")
