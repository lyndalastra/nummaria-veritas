from nummaria_veritas.ingestion.chunking import _split_into_blocks, chunk_page
from nummaria_veritas.models import Page


def test_empty_page_returns_no_chunks() -> None:
    page = Page(
        document_id="test_document",
        page_number=1,
        text="",
    )

    chunks = chunk_page(page)

    assert chunks == []


def test_short_page_returns_single_chunk() -> None:
    page = Page(
        document_id="test_document",
        page_number=1,
        text="Short financial statement.",
    )

    chunks = chunk_page(page)

    assert len(chunks) == 1
    assert chunks[0].text == "Short financial statement."


def test_chunk_preserves_provenance() -> None:
    page = Page(
        document_id="test_document",
        page_number=7,
        text="Revenue increased during the period.",
    )

    chunks = chunk_page(page)

    chunk = chunks[0]

    assert chunk.document_id == "test_document"
    assert chunk.page_number == 7
    assert chunk.chunk_index == 0


def test_long_page_creates_multiple_chunks() -> None:
    page = Page(
        document_id="test_document",
        page_number=1,
        text=("Revenue increased.\n" * 500),
    )

    chunks = chunk_page(
        page,
        max_chars=500,
        overlap_chars=50,
    )

    assert len(chunks) > 1


def test_chunk_ids_are_unique() -> None:
    page = Page(
        document_id="test_document",
        page_number=3,
        text=("Financial statement.\n" * 500),
    )

    chunks = chunk_page(
        page,
        max_chars=500,
        overlap_chars=50,
    )

    chunk_ids = [chunk.chunk_id for chunk in chunks]

    assert len(chunk_ids) == len(set(chunk_ids))


def test_split_into_blocks_preserves_complete_blocks() -> None:
    text = "First block.\n\nSecond block.\n\nThird block."

    blocks = _split_into_blocks(text)

    assert blocks == [
        "First block.",
        "Second block.",
        "Third block.",
    ]
