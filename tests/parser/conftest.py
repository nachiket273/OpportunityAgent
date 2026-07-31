# tests/conftest.py

from pathlib import Path

import fitz


def create_pdf(path: Path, pages: list[str]) -> None:
    doc = fitz.open()

    for text in pages:
        page = doc.new_page()
        page.insert_text((72, 72), text)

    doc.save(path)
    doc.close()
