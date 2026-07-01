"""Tiny Tkinter GUI wrapper around the CLI workflow."""

from __future__ import annotations

from pathlib import Path
from tkinter import BooleanVar, Button, Checkbutton, Entry, Label, StringVar, Tk, messagebox

from ai_readable_pdf_capture.capture import ComplianceError, capture_pages
from ai_readable_pdf_capture.models import CaptureConfig, parse_advance, parse_region
from ai_readable_pdf_capture.pdf_builder import PdfBuildOptions, build_pdf


def launch_gui() -> None:
    root = Tk()
    root.title("AI Readable PDF Capture")

    pages_var = StringVar(value="5")
    region_var = StringVar(value="")
    advance_var = StringVar(value="key:right")
    output_var = StringVar(value="outputs/gui-capture.pdf")
    owner_var = StringVar(value="private-use-only")
    ack_var = BooleanVar(value=False)
    ocr_var = BooleanVar(value=False)

    rows = [
        ("Pages", pages_var),
        ("Region x,y,w,h (blank = fullscreen)", region_var),
        ("Advance: key:right / click:x,y / none", advance_var),
        ("Output PDF", output_var),
        ("Owner label", owner_var),
    ]

    for row, (label_text, variable) in enumerate(rows):
        Label(root, text=label_text).grid(row=row, column=0, sticky="w", padx=8, pady=4)
        Entry(root, textvariable=variable, width=48).grid(row=row, column=1, padx=8, pady=4)

    Checkbutton(root, text="OCR", variable=ocr_var).grid(row=len(rows), column=0, sticky="w", padx=8)
    Checkbutton(
        root,
        text="I will use this only for permitted materials",
        variable=ack_var,
    ).grid(row=len(rows), column=1, sticky="w", padx=8)

    def run_capture() -> None:
        try:
            output_pdf = Path(output_var.get())
            pages_dir = output_pdf.parent / "pages"
            config = CaptureConfig(
                pages=int(pages_var.get()),
                output_dir=pages_dir,
                advance=parse_advance(advance_var.get()),
                region=parse_region(region_var.get() or None),
                acknowledge_compliance=ack_var.get(),
            )
            images = capture_pages(config)
            build_pdf(
                images,
                PdfBuildOptions(
                    output_pdf=output_pdf,
                    ocr=ocr_var.get(),
                    owner_label=owner_var.get(),
                    qr_metadata=owner_var.get(),
                ),
            )
        except ComplianceError as exc:
            messagebox.showerror("Compliance acknowledgement required", str(exc))
            return
        except Exception as exc:  # noqa: BLE001 - GUI should show all user-facing errors.
            messagebox.showerror("Capture failed", str(exc))
            return
        messagebox.showinfo("Done", f"Created {output_pdf}")

    Button(root, text="Start", command=run_capture).grid(
        row=len(rows) + 1, column=0, columnspan=2, pady=12
    )
    root.mainloop()
