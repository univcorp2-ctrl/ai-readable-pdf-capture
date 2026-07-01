from __future__ import annotations

from pathlib import Path

import pytest

from ai_readable_pdf_capture.capture import ComplianceError, capture_pages
from ai_readable_pdf_capture.models import AdvanceAction, CaptureConfig


def test_capture_requires_ack_for_real_capture(tmp_path: Path) -> None:
    config = CaptureConfig(
        pages=1,
        output_dir=tmp_path,
        advance=AdvanceAction(kind="none"),
        start_delay=0,
    )
    with pytest.raises(ComplianceError):
        capture_pages(config)


def test_dry_run_capture(tmp_path: Path) -> None:
    images = capture_pages(
        CaptureConfig(
            pages=2,
            output_dir=tmp_path,
            advance=AdvanceAction(kind="none"),
            dry_run=True,
            start_delay=0,
        )
    )
    assert len(images) == 2
    assert all(path.exists() for path in images)
