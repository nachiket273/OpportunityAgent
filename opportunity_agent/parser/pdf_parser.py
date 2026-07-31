from __future__ import annotations

from pathlib import Path

import fitz

from opportunity_agent.parser.models import ParsedDocument


class PDFParsingError(Exception):
    """Raised when a PDF cannot be parsed."""


def extract_text(pdf_path: str | Path) -> str:
    """
    Extract text from a PDF.

    Parameters
    ----------
    pdf_path
        Path to the PDF.

    Returns
    -------
    str
        Combined text from all pages.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Input file must be a PDF.")

    try:
        document = fitz.open(pdf_path)
    except Exception as exc:
        raise PDFParsingError(f"Unable to open PDF: {pdf_path}") from exc

    pages: list[str] = []

    num_pages = len(document)

    for page in document:
        pages.append(page.get_text())

    document.close()

    return ParsedDocument(text="\n".join(pages), page_count=num_pages)
