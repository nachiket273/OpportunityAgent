import pytest

from opportunity_agent.parser.pdf_parser import (
    PDFParsingError,
    extract_text,
)
from tests.parser.conftest import create_pdf


def test_extract_single_page(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    create_pdf(pdf_path, ["Hello World"])
    parsed = extract_text(pdf_path)
    assert "Hello World" in parsed.text
    assert parsed.page_count == 1
    pdf_path.unlink()


def test_extract_multiple_pages(tmp_path):
    pdf_path = tmp_path / "multi.pdf"
    create_pdf(pdf_path, ["Page One", "Page Two"])
    parsed = extract_text(pdf_path)
    assert "Page One" in parsed.text
    assert "Page Two" in parsed.text
    assert parsed.page_count == 2
    pdf_path.unlink()


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        extract_text("missing.pdf")


def test_non_pdf_file(tmp_path):
    txt = tmp_path / "test.txt"
    txt.write_text("Hello")

    with pytest.raises(ValueError):
        extract_text(txt)

    txt.unlink()


def test_invalid_pdf(tmp_path):
    pdf_path = tmp_path / "bad.pdf"
    pdf_path.write_text("Not a pdf actually!!!")

    with pytest.raises(PDFParsingError):
        extract_text(pdf_path)

    pdf_path.unlink()


def test_empty_pdf(tmp_path):
    pdf_path = tmp_path / "empty.pdf"
    create_pdf(pdf_path, [""])
    parsed = extract_text(pdf_path)
    assert parsed.text == ""
    assert parsed.page_count == 1
    pdf_path.unlink()


def test_unicode(tmp_path):
    pdf_path = tmp_path / "unicode.pdf"
    txt = "España München"
    create_pdf(pdf_path, [txt])

    parsed = extract_text(pdf_path)

    assert "España" in parsed.text
    assert "München" in parsed.text
    assert parsed.page_count == 1
    pdf_path.unlink()
