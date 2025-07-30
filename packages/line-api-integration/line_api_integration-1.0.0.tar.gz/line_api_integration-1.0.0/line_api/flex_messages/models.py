"""
LINE Flex Message models and schemas.

This module provides Pydantic models for creating type-safe Flex Messages
that can be used with the LINE Messaging API.
"""

from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field


class FlexMessageType(str, Enum):
    """Flex message types."""

    BUBBLE = "bubble"
    CAROUSEL = "carousel"


class FlexPosition(str, Enum):
    """Flex position options."""

    RELATIVE = "relative"
    ABSOLUTE = "absolute"


class FlexAlignment(str, Enum):
    """Flex alignment options."""

    START = "start"
    END = "end"
    CENTER = "center"


class FlexLayout(str, Enum):
    """Flex container layouts."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    BASELINE = "baseline"


class FlexButtonStyle(str, Enum):
    """Button styles."""

    LINK = "link"
    PRIMARY = "primary"
    SECONDARY = "secondary"


class FlexAction(BaseModel):
    """Base flex action."""

    type: str

    model_config = {"extra": "forbid"}


class FlexPostbackAction(FlexAction):
    """Postback action."""

    type: str = Field(default="postback", frozen=True)
    label: Optional[str] = None
    data: str
    display_text: Optional[str] = Field(default=None, alias="displayText")


class FlexMessageAction(FlexAction):
    """Message action."""

    type: str = Field(default="message", frozen=True)
    label: Optional[str] = None
    text: str


class FlexUriAction(FlexAction):
    """URI action."""

    type: str = Field(default="uri", frozen=True)
    label: Optional[str] = None
    uri: str
    alt_uri_desktop: Optional[str] = Field(default=None, alias="altUriDesktop")


class FlexComponent(BaseModel):
    """Base flex component."""

    type: str

    model_config = {"extra": "forbid"}


class FlexText(FlexComponent):
    """Text component."""

    type: str = Field(default="text", frozen=True)
    text: str
    size: Optional[str] = None
    weight: Optional[str] = None
    color: Optional[str] = None
    align: Optional[str] = None
    gravity: Optional[str] = None
    wrap: Optional[bool] = None
    max_lines: Optional[int] = Field(default=None, alias="maxLines")
    flex: Optional[int] = None
    margin: Optional[str] = None
    offset_top: Optional[str] = Field(default=None, alias="offsetTop")
    offset_bottom: Optional[str] = Field(default=None, alias="offsetBottom")
    offset_start: Optional[str] = Field(default=None, alias="offsetStart")
    offset_end: Optional[str] = Field(default=None, alias="offsetEnd")
    action: Optional[Union[FlexPostbackAction, FlexMessageAction, FlexUriAction]] = None

    @classmethod
    def create(
        cls,
        text: str,
        *,
        size: Optional[str] = None,
        weight: Optional[str] = None,
        color: Optional[str] = None,
        align: Optional[str] = None,
        wrap: Optional[bool] = None,
        flex: Optional[int] = None,
        action: Optional[
            Union[FlexPostbackAction, FlexMessageAction, FlexUriAction]
        ] = None,
    ) -> "FlexText":
        """Create a FlexText component with the given parameters."""
        return cls(
            text=text,
            size=size,
            weight=weight,
            color=color,
            align=align,
            wrap=wrap,
            flex=flex,
            action=action,
        )


class FlexButton(FlexComponent):
    """Button component."""

    type: str = Field(default="button", frozen=True)
    action: Union[FlexPostbackAction, FlexMessageAction, FlexUriAction]
    style: Optional[FlexButtonStyle] = None
    color: Optional[str] = None
    gravity: Optional[str] = None

    @classmethod
    def create(
        cls,
        action: Union[FlexPostbackAction, FlexMessageAction, FlexUriAction],
        *,
        style: Optional[FlexButtonStyle] = None,
        color: Optional[str] = None,
        gravity: Optional[str] = None,
    ) -> "FlexButton":
        """Create a FlexButton component with the given parameters."""
        return cls(
            action=action,
            style=style,
            color=color,
            gravity=gravity,
        )


class FlexImage(FlexComponent):
    """Image component."""

    type: str = Field(default="image", frozen=True)
    url: str
    position: Optional[FlexPosition] = None
    margin: Optional[str] = None
    size: Optional[str] = None
    aspect_ratio: Optional[str] = Field(default=None, alias="aspectRatio")
    aspect_mode: Optional[str] = Field(default=None, alias="aspectMode")
    background_color: Optional[str] = Field(default=None, alias="backgroundColor")
    gravity: Optional[str] = None
    flex: Optional[int] = None
    align: Optional[Union[FlexAlignment, str]] = None
    offset_top: Optional[str] = Field(default=None, alias="offsetTop")
    offset_bottom: Optional[str] = Field(default=None, alias="offsetBottom")
    offset_start: Optional[str] = Field(default=None, alias="offsetStart")
    offset_end: Optional[str] = Field(default=None, alias="offsetEnd")
    action: Optional[Union[FlexPostbackAction, FlexMessageAction, FlexUriAction]] = None

    @classmethod
    def create(
        cls,
        url: str,
        *,
        size: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        aspect_mode: Optional[str] = None,
        gravity: Optional[str] = None,
        flex: Optional[int] = None,
        action: Optional[
            Union[FlexPostbackAction, FlexMessageAction, FlexUriAction]
        ] = None,
    ) -> "FlexImage":
        """Create a FlexImage component with the given parameters."""
        return cls(
            url=url,
            size=size,
            aspectRatio=aspect_ratio,
            aspectMode=aspect_mode,
            gravity=gravity,
            flex=flex,
            action=action,
        )


class FlexSeparator(FlexComponent):
    """Separator component."""

    type: str = Field(default="separator", frozen=True)
    margin: Optional[str] = None
    color: Optional[str] = None

    @classmethod
    def create(
        cls, *, margin: Optional[str] = None, color: Optional[str] = None,
    ) -> "FlexSeparator":
        """Create a FlexSeparator component with the given parameters."""
        return cls(margin=margin, color=color)


class FlexBox(FlexComponent):
    """Box container component."""

    type: str = Field(default="box", frozen=True)
    layout: FlexLayout
    contents: list[Union[FlexText, FlexButton, FlexImage, FlexSeparator, "FlexBox"]]
    flex: Optional[int] = None
    spacing: Optional[str] = None
    margin: Optional[str] = None
    padding_all: Optional[str] = Field(default=None, alias="paddingAll")
    padding_top: Optional[str] = Field(default=None, alias="paddingTop")
    padding_bottom: Optional[str] = Field(default=None, alias="paddingBottom")
    padding_start: Optional[str] = Field(default=None, alias="paddingStart")
    padding_end: Optional[str] = Field(default=None, alias="paddingEnd")
    background_color: Optional[str] = Field(default=None, alias="backgroundColor")
    border_color: Optional[str] = Field(default=None, alias="borderColor")
    border_width: Optional[str] = Field(default=None, alias="borderWidth")
    corner_radius: Optional[str] = Field(default=None, alias="cornerRadius")
    offset_top: Optional[str] = Field(default=None, alias="offsetTop")
    offset_bottom: Optional[str] = Field(default=None, alias="offsetBottom")
    offset_start: Optional[str] = Field(default=None, alias="offsetStart")
    offset_end: Optional[str] = Field(default=None, alias="offsetEnd")

    @classmethod
    def create(
        cls,
        layout: FlexLayout,
        contents: list[
            Union[FlexText, FlexButton, FlexImage, FlexSeparator, "FlexBox"]
        ],
        *,
        flex: Optional[int] = None,
        spacing: Optional[str] = None,
        margin: Optional[str] = None,
        padding_all: Optional[str] = None,
        background_color: Optional[str] = None,
    ) -> "FlexBox":
        """Create a FlexBox component with the given parameters."""
        return cls(
            layout=layout,
            contents=contents,
            flex=flex,
            spacing=spacing,
            margin=margin,
            paddingAll=padding_all,
            backgroundColor=background_color,
        )


class FlexBubble(BaseModel):
    """Flex bubble container."""

    type: str = Field(default="bubble", frozen=True)
    size: Optional[str] = None
    direction: Optional[str] = None
    header: Optional[FlexBox] = None
    hero: Optional[Union[FlexImage, FlexBox]] = None
    body: Optional[FlexBox] = None
    footer: Optional[FlexBox] = None
    styles: Optional[dict[str, Any]] = None

    @classmethod
    def create(
        cls,
        *,
        header: Optional[FlexBox] = None,
        hero: Optional[Union[FlexImage, FlexBox]] = None,
        body: Optional[FlexBox] = None,
        footer: Optional[FlexBox] = None,
        size: Optional[str] = None,
        styles: Optional[dict[str, Any]] = None,
    ) -> "FlexBubble":
        """Create a FlexBubble with the given components."""
        return cls(
            header=header,
            hero=hero,
            body=body,
            footer=footer,
            size=size,
            styles=styles,
        )


class FlexCarousel(BaseModel):
    """Flex carousel container."""

    type: str = Field(default="carousel", frozen=True)
    contents: list[FlexBubble]

    @classmethod
    def create(cls, bubbles: list[FlexBubble]) -> "FlexCarousel":
        """Create a FlexCarousel with the given bubbles."""
        return cls(contents=bubbles)


class FlexMessage(BaseModel):
    """Main flex message structure."""

    type: str = Field(default="flex", frozen=True)
    alt_text: str = Field(alias="altText")
    contents: Union[FlexBubble, FlexCarousel]

    @classmethod
    def create(
        cls,
        alt_text: str,
        contents: Union[FlexBubble, FlexCarousel],
    ) -> "FlexMessage":
        """Create a FlexMessage with the given alt text and contents."""
        return cls(altText=alt_text, contents=contents)
