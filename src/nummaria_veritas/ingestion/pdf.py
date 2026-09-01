from pathlib import Path

import pymupdf

from nummaria_veritas.models import Document, Page


def extract_pages(document: Document) -> list[Page]:
    source_path = Path(document.source_path)

    if not source_path.exists():
        raise FileNotFoundError(f"Source PDF does not exist: {source_path}")

    pages: list[Page] = []

    with pymupdf.open(source_path) as pdf:
        for index, pdf_page in enumerate(pdf):
            text = pdf_page.get_text("text").strip()

            pages.append(
                Page(
                    document_id=document.document_id,
                    page_number=index + 1,
                    text=text,
                )
            )

    return pages
