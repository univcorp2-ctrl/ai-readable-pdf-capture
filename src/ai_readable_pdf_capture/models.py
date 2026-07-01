"""Data models and parsing helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

AdvanceKind = Literal["key", "click", "none"]


@dataclass(frozen=True)
class Region:
    """A screen capture rectangle."""

    x: int
    y: int
    width: int
    height: int

    def as_tuple(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)


@dataclass(frozen=True)
class AdvanceAction:
    """How to move to the next page after each screenshot."""

    kind: AdvanceKind
    value: str | tuple[int, int] | None = None


@dataclass(frozen=True)
class CaptureConfig:
    """Configuration for capture + PDF build workflow."""

    pages: int
    output_dir: Path
    advance: AdvanceAction
    delay: float = 0.5
    start_delay: float = 3.0
    region: Region | None = None
    prefix: str = "page"
    acknowledge_compliance: bool = False
    dry_run: bool = False


def parse_region(value: str | None) -> Region | None:
    """Parse `x,y,width,height` into a Region."""

    if value is None or value.strip() == "":
        return None
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise ValueError("region must be formatted as x,y,width,height")
    try:
        x, y, width, height = (int(part) for part in parts)
    except ValueError as exc:
        raise ValueError("region values must be integers") from exc
    if width <= 0 or height <= 0:
        raise ValueError("region width and height must be positive")
    return Region(x=x, y=y, width=width, height=height)


def parse_advance(value: str) -> AdvanceAction:
    """Parse an advance action.

    Supported formats:
    - key:right
    - key:left
    - key:pagedown
    - click:1200,800
    - none
    """

    normalized = value.strip().lower()
    if normalized in {"", "none", "no", "off"}:
        return AdvanceAction(kind="none")
    if normalized.startswith("key:"):
        key = normalized.removeprefix("key:").strip()
        if not key:
            raise ValueError("key advance requires a key name, for example key:right")
        return AdvanceAction(kind="key", value=key)
    if normalized.startswith("click:"):
        coords = normalized.removeprefix("click:").split(",")
        if len(coords) != 2:
            raise ValueError("click advance must be formatted as click:x,y")
        try:
            x, y = (int(coord.strip()) for coord in coords)
        except ValueError as exc:
            raise ValueError("click coordinates must be integers") from exc
        return AdvanceAction(kind="click", value=(x, y))
    raise ValueError("advance must be one of key:<name>, click:x,y, or none")
