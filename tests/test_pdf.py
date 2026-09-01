from pathlib import Path

from nummaria_veritas.ingestion.manifest import load_document_manifest
from nummaria_veritas.ingestion.pdf import extract_pages

MANIFEST_PATH = Path("configs/documents.yaml")


def test_pdf_extraction_returns_pages() -> None:
    document = load_document_manifest(MANIFEST_PATH)[0]

    pages = extract_pages(document)

    assert pages


def test_page_numbers_start_at_one() -> None:
    document = load_document_manifest(MANIFEST_PATH)[0]

    pages = extract_pages(document)

    assert pages[0].page_number == 1


def test_page_numbers_are_sequential() -> None:
    document = load_document_manifest(MANIFEST_PATH)[0]

    pages = extract_pages(document)

    page_numbers = [page.page_number for page in pages]

    assert page_numbers == list(range(1, len(pages) + 1))


def test_pages_preserve_document_id() -> None:
    document = load_document_manifest(MANIFEST_PATH)[0]

    pages = extract_pages(document)

    assert all(page.document_id == document.document_id for page in pages)
