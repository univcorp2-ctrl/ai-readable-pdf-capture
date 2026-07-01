"""YAML configuration loader."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ai_readable_pdf_capture.models import CaptureConfig, parse_advance, parse_region


def load_capture_config(path: Path) -> CaptureConfig:
    """Load capture config from YAML."""

    with path.open("r", encoding="utf-8") as handle:
        data: dict[str, Any] = yaml.safe_load(handle) or {}

    output_dir = Path(data.get("output_dir", "outputs/pages"))
    advance = parse_advance(str(data.get("advance", "key:right")))
    region = parse_region(data.get("region"))
    return CaptureConfig(
        pages=int(data.get("pages", 1)),
        output_dir=output_dir,
        advance=advance,
        delay=float(data.get("delay", 0.5)),
        start_delay=float(data.get("start_delay", 3.0)),
        region=region,
        prefix=str(data.get("prefix", "page")),
        acknowledge_compliance=bool(data.get("acknowledge_compliance", False)),
        dry_run=bool(data.get("dry_run", False)),
    )
