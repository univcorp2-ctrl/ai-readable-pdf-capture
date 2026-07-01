"""PDF generation with optional OCR text layer, watermark, QR, and metadata."""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

import qrcode
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas


@dataclass(frozen=True)
class OcrWord:
    text: str
    x: int
    y: int
    width: int
    height: int
    confidence: float


@dataclass(frozen=True)
class PdfBuildOptions:
    output_pdf: Path
    ocr: bool = False
    language: str = "eng+jpn"
    owner_label: str = ""
    title: str = "AI Readable PDF Capture"
    qr_metadata: str = ""
    min_confidence: float = 30.0


def _sorted_images(paths: list[Path] | tuple[Path, ...]) -> list[Path]:
    images = [Path(path) for path in paths]
    if not images:
        raise ValueError("At least one image is required")
    for image in images:
        if not image.exists():
            raise FileNotFoundError(image)
    return sorted(images)


def _register_ocr_font() -> str:
    """Register a CID font that can carry Japanese text when available."""

    font_name = "HeiseiMin-W3"
    try:
        pdfmetrics.getFont(font_name)
    except KeyError:
        try:
            pdfmetrics.registerFont(UnicodeCIDFont(font_name))
        except Exception:
            return "Helvetica"
    return font_name


def _ocr_words(image_path: Path, language: str, min_confidence: float) -> list[OcrWord]:
    """Extract OCR word boxes using Tesseract if available."""

    try:
        import pytesseract
        from pytesseract import Output
    except ImportError as exc:
        raise RuntimeError("pytesseract is not installed") from exc

    try:
        data = pytesseract.image_to_data(
            Image.open(image_path), lang=language, output_type=Output.DICT
        )
    except pytesseract.TesseractNotFoundError as exc:
        raise RuntimeError(
            "Tesseract executable was not found. Install Tesseract OCR or run without --ocr."
        ) from exc

    words: list[OcrWord] = []
    for i, text in enumerate(data.get("text", [])):
        clean_text = str(text).strip()
        if not clean_text:
            continue
        try:
            confidence = float(data["conf"][i])
        except (ValueError, TypeError):
            confidence = -1.0
        if confidence < min_confidence:
            continue
        words.append(
            OcrWord(
                text=clean_text,
                x=int(data["left"][i]),
                y=int(data["top"][i]),
                width=int(data["width"][i]),
                height=int(data["height"][i]),
                confidence=confidence,
            )
        )
    return words


def _draw_owner_label(pdf: canvas.Canvas, width: int, height: int, owner_label: str) -> None:
    if not owner_label:
        return
    pdf.saveState()
    try:
        pdf.setFillAlpha(0.30)
    except AttributeError:
        pass
    pdf.setFillColorRGB(0.1, 0.1, 0.1)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(24, 18, owner_label[:180])
    pdf.restoreState()


def _draw_qr(pdf: canvas.Canvas, width: int, qr_metadata: str) -> None:
    if not qr_metadata:
        return
    qr_image = qrcode.make(qr_metadata)
    buffer = io.BytesIO()
    qr_image.save(buffer, format="PNG")
    buffer.seek(0)
    size = 64
    pdf.drawImage(ImageReader(buffer), width - size - 18, 18, size, size, mask="auto")


def _draw_invisible_ocr_text(
    pdf: canvas.Canvas,
    image_path: Path,
    page_height: int,
    language: str,
    min_confidence: float,
) -> None:
    font_name = _register_ocr_font()
    words = _ocr_words(image_path, language=language, min_confidence=min_confidence)
    text_object = pdf.beginText()
    text_object.setTextRenderMode(3)  # Invisible text. Keeps PDF searchable/selectable.
    for word in words:
        font_size = max(4, min(48, int(word.height * 0.85)))
        text_object.setFont(font_name, font_size)
        text_object.setTextOrigin(word.x, page_height - word.y - word.height)
        try:
            text_object.textLine(word.text)
        except Exception:
            # Some fonts/codepoints may not be encodable in a given ReportLab installation.
            continue
    pdf.drawText(text_object)


def _add_metadata(input_pdf: Path, output_pdf: Path, options: PdfBuildOptions) -> None:
    reader = PdfReader(str(input_pdf))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata(
        {
            "/Title": options.title,
            "/Producer": "AI Readable PDF Capture",
            "/Subject": "Searchable PDF generated from permitted screenshots/images",
            "/Keywords": "ai,pdf,ocr,screen-capture,compliant-use",
        }
    )
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with output_pdf.open("wb") as handle:
        writer.write(handle)


def build_pdf(image_paths: list[Path] | tuple[Path, ...], options: PdfBuildOptions) -> Path:
    """Build a PDF from images and optionally add an invisible OCR text layer."""

    images = _sorted_images(image_paths)
    options.output_pdf.parent.mkdir(parents=True, exist_ok=True)

    with NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_path = Path(temp_file.name)

    pdf = canvas.Canvas(str(temp_path), pageCompression=1)
    pdf.setTitle(options.title)

    try:
        for image_path in images:
            with Image.open(image_path) as image:
                image = image.convert("RGB")
                width, height = image.size
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                buffer.seek(0)

            pdf.setPageSize((width, height))
            pdf.drawImage(ImageReader(buffer), 0, 0, width=width, height=height)
            if options.ocr:
                _draw_invisible_ocr_text(
                    pdf,
                    image_path=image_path,
                    page_height=height,
                    language=options.language,
                    min_confidence=options.min_confidence,
                )
            _draw_owner_label(pdf, width=width, height=height, owner_label=options.owner_label)
            qr_payload = options.qr_metadata or options.owner_label
            _draw_qr(pdf, width=width, qr_metadata=qr_payload)
            pdf.showPage()
        pdf.save()
        _add_metadata(temp_path, options.output_pdf, options)
    finally:
        temp_path.unlink(missing_ok=True)

    return options.output_pdf


def collect_images(input_path: Path) -> list[Path]:
    """Collect supported images from a directory or a single image path."""

    supported = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
    if input_path.is_file():
        if input_path.suffix.lower() not in supported:
            raise ValueError(f"Unsupported image type: {input_path.suffix}")
        return [input_path]
    if not input_path.exists():
        raise FileNotFoundError(input_path)
    images = [path for path in input_path.iterdir() if path.suffix.lower() in supported]
    if not images:
        raise ValueError(f"No supported images found in {input_path}")
    return sorted(images)
