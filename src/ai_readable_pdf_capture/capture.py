"""Screen capture automation."""

from __future__ import annotations

import time
from pathlib import Path

from PIL import Image, ImageDraw

from ai_readable_pdf_capture.models import AdvanceAction, CaptureConfig


class ComplianceError(RuntimeError):
    """Raised when capture is requested without explicit compliance acknowledgement."""


def ensure_compliance_acknowledged(config: CaptureConfig) -> None:
    """Block real screen capture until the user explicitly acknowledges compliant use."""

    if config.dry_run:
        return
    if not config.acknowledge_compliance:
        raise ComplianceError(
            "Real screen capture requires --acknowledge-compliance. Use this only for materials "
            "you own, are authorized to capture, or whose terms permit capture."
        )


def perform_advance(action: AdvanceAction) -> None:
    """Send the configured page advance action."""

    if action.kind == "none":
        return

    import pyautogui  # Imported lazily so tests and CI can run headlessly.

    if action.kind == "key":
        assert isinstance(action.value, str)
        pyautogui.press(action.value)
        return
    if action.kind == "click":
        assert isinstance(action.value, tuple)
        pyautogui.click(*action.value)
        return
    raise ValueError(f"Unsupported advance action: {action.kind}")


def _write_dry_run_page(path: Path, page_number: int, size: tuple[int, int] = (900, 1200)) -> None:
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((40, 40, size[0] - 40, size[1] - 40), outline="#2563eb", width=4)
    draw.text((80, 100), f"Demo capture page {page_number}", fill="#111827")
    draw.text(
        (80, 160),
        "This is generated sample content for CI and local testing.",
        fill="#374151",
    )
    draw.text((80, 220), "Use real capture only for permitted materials.", fill="#b91c1c")
    image.save(path)


def capture_pages(config: CaptureConfig) -> list[Path]:
    """Capture pages according to config and return image paths."""

    if config.pages <= 0:
        raise ValueError("pages must be positive")

    ensure_compliance_acknowledged(config)
    config.output_dir.mkdir(parents=True, exist_ok=True)
    captured: list[Path] = []

    if config.start_delay > 0 and not config.dry_run:
        time.sleep(config.start_delay)

    for index in range(1, config.pages + 1):
        path = config.output_dir / f"{config.prefix}_{index:04d}.png"
        if config.dry_run:
            _write_dry_run_page(path, index)
        else:
            import pyautogui  # Imported lazily so tests and CI can run headlessly.

            screenshot = pyautogui.screenshot(region=config.region.as_tuple() if config.region else None)
            screenshot.save(path)
        captured.append(path)

        if index < config.pages:
            perform_advance(config.advance)
            if config.delay > 0 and not config.dry_run:
                time.sleep(config.delay)

    return captured
