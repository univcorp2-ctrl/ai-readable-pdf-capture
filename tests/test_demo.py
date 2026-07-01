from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from ai_readable_pdf_capture.demo import create_demo


def test_create_demo(tmp_path: Path) -> None:
    pdf = create_demo(tmp_path)
    assert pdf.exists()
    assert len(PdfReader(str(pdf)).pages) == 3
    assert (tmp_path / "pages" / "page_0001.png").exists()
