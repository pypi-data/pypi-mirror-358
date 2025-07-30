from typing_extensions import Literal, Required, TypedDict, Optional, Union


class TextBlock(TypedDict, total=False):
    text: Required[str]
    """The text content."""

    type: Required[Literal["text"]]
    """The type of the content part."""

    uid: Optional[str]
    """An optional unique identifier for the content part."""


class ImageBlock(TypedDict, total=False):
    image_url: Required[str]
    """The URL of the image."""

    type: Required[Literal["image"]]
    """The type of the content part."""

    uid: Required[str]
    """A unique identifier for the content part."""


class PlotlyJsonBlock(TypedDict, total=False):
    plotly_json: Required[dict]
    """The Plotly JSON data."""

    type: Required[Literal["plotly-json"]]
    """The type of the content part."""

    image_url: Required[str]
    """The URL of the image representation of the Plotly chart."""

    uid: Required[str]
    """A unique identifier for the content part."""


class HtmlBlock(TypedDict, total=False):
    html: Required[str]
    """The HTML content."""

    type: Required[Literal["html"]]
    """The type of the content part."""

    uid: Optional[str]
    """An optional unique identifier for the content part."""


class JsonBlock(TypedDict, total=False):
    json: Required[dict]
    """The JSON content."""

    type: Required[Literal["json"]]
    """The type of the content part."""

    uid: Optional[str]
    """An optional unique identifier for the content part."""

Block = Union[
    TextBlock,
    ImageBlock,
    PlotlyJsonBlock,
    HtmlBlock,
    JsonBlock,
]
