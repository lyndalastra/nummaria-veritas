from datetime import date
from pathlib import Path

from nummaria_veritas.retrieval.corpus import (
    filter_chunks_as_of,
    load_chunks,
)

CHUNKS_PATH = Path("data/processed/chunks.jsonl")


def test_processed_corpus_loads() -> None:
    chunks = load_chunks(CHUNKS_PATH)

    assert chunks


def test_temporal_filter_excludes_future_documents() -> None:
    chunks = load_chunks(CHUNKS_PATH)

    company = chunks[0].company
    company_chunks = [chunk for chunk in chunks if chunk.company == company]

    cutoff = min(chunk.publication_date for chunk in company_chunks)

    filtered = filter_chunks_as_of(
        chunks,
        company=company,
        as_of_date=cutoff,
    )

    assert filtered
    assert all(chunk.publication_date <= cutoff for chunk in filtered)


def test_temporal_filter_respects_company() -> None:
    chunks = load_chunks(CHUNKS_PATH)

    company = chunks[0].company

    cutoff = max(chunk.publication_date for chunk in chunks if chunk.company == company)

    filtered = filter_chunks_as_of(
        chunks,
        company=company,
        as_of_date=cutoff,
    )

    assert filtered
    assert all(chunk.company == company for chunk in filtered)


def test_earliest_cutoff_excludes_later_documents() -> None:
    chunks = load_chunks(CHUNKS_PATH)

    company = chunks[0].company
    company_chunks = [chunk for chunk in chunks if chunk.company == company]

    publication_dates = {chunk.publication_date for chunk in company_chunks}

    if len(publication_dates) < 2:
        return

    earliest_date = min(publication_dates)

    filtered = filter_chunks_as_of(
        chunks,
        company=company,
        as_of_date=earliest_date,
    )

    assert filtered
    assert all(chunk.publication_date == earliest_date for chunk in filtered)


def test_cutoff_before_first_publication_returns_no_chunks() -> None:
    chunks = load_chunks(CHUNKS_PATH)

    company = chunks[0].company
    company_chunks = [chunk for chunk in chunks if chunk.company == company]

    earliest_date = min(chunk.publication_date for chunk in company_chunks)

    cutoff = date(
        earliest_date.year - 1,
        earliest_date.month,
        earliest_date.day,
    )

    filtered = filter_chunks_as_of(
        chunks,
        company=company,
        as_of_date=cutoff,
    )

    assert filtered == []
