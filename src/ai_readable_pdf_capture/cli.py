"""Command line interface."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from ai_readable_pdf_capture.capture import ComplianceError, capture_pages
from ai_readable_pdf_capture.config import load_capture_config
from ai_readable_pdf_capture.demo import create_demo
from ai_readable_pdf_capture.gui import launch_gui
from ai_readable_pdf_capture.models import CaptureConfig, parse_advance, parse_region
from ai_readable_pdf_capture.pdf_builder import PdfBuildOptions, build_pdf, collect_images

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()


@app.command()
def demo(output_dir: Path = typer.Option(Path("outputs/demo"), help="Demo output directory.")) -> None:
    """Generate demo images and a demo PDF without screen capture."""

    pdf = create_demo(output_dir)
    console.print(f"[green]Created demo PDF:[/] {pdf}")


@app.command()
def capture(
    pages: int = typer.Option(..., min=1, help="Number of pages/screenshots to capture."),
    output_dir: Path = typer.Option(Path("outputs/pages"), help="Directory for captured images."),
    advance: str = typer.Option("key:right", help="key:<name>, click:x,y, or none."),
    delay: float = typer.Option(0.5, min=0, help="Delay after page advance."),
    start_delay: float = typer.Option(3.0, min=0, help="Initial delay before first capture."),
    region: str | None = typer.Option(None, help="Capture region formatted as x,y,width,height."),
    prefix: str = typer.Option("page", help="Image filename prefix."),
    acknowledge_compliance: bool = typer.Option(
        False,
        "--acknowledge-compliance",
        help="Required for real capture; confirms permitted/legal use.",
    ),
    dry_run: bool = typer.Option(False, help="Generate sample images instead of screen capture."),
) -> None:
    """Capture page screenshots."""

    config = CaptureConfig(
        pages=pages,
        output_dir=output_dir,
        advance=parse_advance(advance),
        delay=delay,
        start_delay=start_delay,
        region=parse_region(region),
        prefix=prefix,
        acknowledge_compliance=acknowledge_compliance,
        dry_run=dry_run,
    )
    try:
        images = capture_pages(config)
    except ComplianceError as exc:
        raise typer.BadParameter(str(exc)) from exc
    console.print(f"[green]Captured {len(images)} image(s):[/] {output_dir}")


@app.command(name="build")
def build_command(
    input_path: Path = typer.Argument(..., help="Image file or directory."),
    output: Path = typer.Option(Path("outputs/result.pdf"), help="Output PDF path."),
    ocr: bool = typer.Option(False, help="Enable Tesseract OCR invisible text layer."),
    language: str = typer.Option("eng+jpn", help="Tesseract languages, for example eng+jpn."),
    owner_label: str = typer.Option("", help="Owner/watermark label to embed on each page."),
    title: str = typer.Option("AI Readable PDF Capture", help="PDF title metadata."),
    qr_metadata: str = typer.Option("", help="QR metadata; defaults to owner label when blank."),
) -> None:
    """Build PDF from captured images."""

    images = collect_images(input_path)
    pdf = build_pdf(
        images,
        PdfBuildOptions(
            output_pdf=output,
            ocr=ocr,
            language=language,
            owner_label=owner_label,
            title=title,
            qr_metadata=qr_metadata,
        ),
    )
    console.print(f"[green]Created PDF:[/] {pdf}")


@app.command()
def run(
    pages: int = typer.Option(..., min=1, help="Number of pages/screenshots to capture."),
    output: Path = typer.Option(Path("outputs/result.pdf"), help="Output PDF path."),
    advance: str = typer.Option("key:right", help="key:<name>, click:x,y, or none."),
    delay: float = typer.Option(0.5, min=0, help="Delay after page advance."),
    start_delay: float = typer.Option(3.0, min=0, help="Initial delay before first capture."),
    region: str | None = typer.Option(None, help="Capture region formatted as x,y,width,height."),
    ocr: bool = typer.Option(False, help="Enable Tesseract OCR invisible text layer."),
    language: str = typer.Option("eng+jpn", help="Tesseract languages, for example eng+jpn."),
    owner_label: str = typer.Option("", help="Owner/watermark label to embed on each page."),
    acknowledge_compliance: bool = typer.Option(
        False,
        "--acknowledge-compliance",
        help="Required for real capture; confirms permitted/legal use.",
    ),
    dry_run: bool = typer.Option(False, help="Generate sample images instead of screen capture."),
) -> None:
    """Capture screenshots and build a PDF in one command."""

    pages_dir = output.parent / "pages"
    config = CaptureConfig(
        pages=pages,
        output_dir=pages_dir,
        advance=parse_advance(advance),
        delay=delay,
        start_delay=start_delay,
        region=parse_region(region),
        acknowledge_compliance=acknowledge_compliance,
        dry_run=dry_run,
    )
    try:
        images = capture_pages(config)
    except ComplianceError as exc:
        raise typer.BadParameter(str(exc)) from exc
    pdf = build_pdf(
        images,
        PdfBuildOptions(
            output_pdf=output,
            ocr=ocr,
            language=language,
            owner_label=owner_label,
            qr_metadata=owner_label,
        ),
    )
    console.print(f"[green]Created PDF:[/] {pdf}")


@app.command()
def from_config(config: Path = typer.Argument(..., help="YAML config path.")) -> None:
    """Capture pages from a YAML config file."""

    capture_config = load_capture_config(config)
    images = capture_pages(capture_config)
    console.print(f"[green]Captured {len(images)} image(s):[/] {capture_config.output_dir}")


@app.command()
def gui() -> None:
    """Launch the optional Tkinter GUI."""

    launch_gui()


if __name__ == "__main__":
    app()
