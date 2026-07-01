"""Demo asset generation."""

from __future__ import annotations

from pathlib import Path

from ai_readable_pdf_capture.capture import capture_pages
from ai_readable_pdf_capture.models import AdvanceAction, CaptureConfig
from ai_readable_pdf_capture.pdf_builder import PdfBuildOptions, build_pdf


def create_demo(output_dir: Path) -> Path:
    """Create a small demo PDF without accessing the user's screen."""

    pages_dir = output_dir / "pages"
    images = capture_pages(
        CaptureConfig(
            pages=3,
            output_dir=pages_dir,
            advance=AdvanceAction(kind="none"),
            dry_run=True,
            acknowledge_compliance=True,
            start_delay=0,
        )
    )
    return build_pdf(
        images,
        PdfBuildOptions(
            output_pdf=output_dir / "demo.pdf",
            owner_label="demo / permitted-use-only",
            title="AI Readable PDF Capture Demo",
            qr_metadata="AI Readable PDF Capture demo; permitted-use-only",
        ),
    )
