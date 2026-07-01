from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader

from ai_readable_pdf_capture.pdf_builder import PdfBuildOptions, build_pdf, collect_images


def _make_image(path: Path, text: str) -> None:
    image = Image.new("RGB", (400, 600), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 80), text, fill="black")
    image.save(path)


def test_collect_images_and_build_pdf(tmp_path: Path) -> None:
    pages_dir = tmp_path / "pages"
    pages_dir.mkdir()
    _make_image(pages_dir / "page_0002.png", "second")
    _make_image(pages_dir / "page_0001.png", "first")

    images = collect_images(pages_dir)
    assert [image.name for image in images] == ["page_0001.png", "page_0002.png"]

    output_pdf = tmp_path / "result.pdf"
    build_pdf(
        images,
        PdfBuildOptions(
            output_pdf=output_pdf,
            owner_label="unit-test / permitted-use-only",
            qr_metadata="unit-test",
        ),
    )

    reader = PdfReader(str(output_pdf))
    assert len(reader.pages) == 2
    assert reader.metadata is not None
    assert reader.metadata.title == "AI Readable PDF Capture"
