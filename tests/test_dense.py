from datetime import date, timedelta

import pytest

from nummaria_veritas.models import IngestedChunk
from nummaria_veritas.retrieval.dense import (
    build_dense_index,
    retrieve_dense,
)


def _make_chunks(count: int = 4) -> list[IngestedChunk]:
    base_date = date.min + timedelta(days=10)

    return [
        IngestedChunk(
            chunk_id=f"chunk_{index}",
            document_id=f"document_{index}",
            company=f"entity_{index % 2}",
            document_type="test_document",
            reporting_period=f"period_{index}",
            publication_date=base_date + timedelta(days=index),
            page_number=index + 1,
            chunk_index=index,
            text=f"test financial content {index}",
        )
        for index in range(count)
    ]


def test_dense_index_contains_all_chunks() -> None:
    chunks = _make_chunks()

    index = build_dense_index(chunks)

    assert len(index.chunks) == len(chunks)
    assert index.embeddings.shape[0] == len(chunks)


def test_dense_index_produces_dense_embeddings() -> None:
    chunks = _make_chunks()

    index = build_dense_index(chunks)

    assert index.embeddings.ndim == 2
    assert index.embeddings.shape[1] > 0


def test_dense_retrieval_excludes_future_evidence() -> None:
    chunks = _make_chunks()

    company = chunks[0].company

    company_chunks = [chunk for chunk in chunks if chunk.company == company]

    cutoff = min(chunk.publication_date for chunk in company_chunks)

    index = build_dense_index(chunks)

    results = retrieve_dense(
        index,
        query=company_chunks[0].text,
        company=company,
        as_of_date=cutoff,
        top_k=len(chunks),
    )

    assert results
    assert all(result.publication_date <= cutoff for result in results)


def test_dense_retrieval_respects_company() -> None:
    chunks = _make_chunks()

    company = chunks[0].company

    cutoff = max(chunk.publication_date for chunk in chunks)

    index = build_dense_index(chunks)

    results = retrieve_dense(
        index,
        query=chunks[0].text,
        company=company,
        as_of_date=cutoff,
        top_k=len(chunks),
    )

    assert results
    assert all(result.company == company for result in results)


def test_dense_retrieval_respects_top_k() -> None:
    chunks = _make_chunks()

    company = chunks[0].company

    eligible_chunks = [chunk for chunk in chunks if chunk.company == company]

    cutoff = max(chunk.publication_date for chunk in eligible_chunks)

    requested_top_k = max(
        1,
        len(eligible_chunks) - 1,
    )

    index = build_dense_index(chunks)

    results = retrieve_dense(
        index,
        query=eligible_chunks[0].text,
        company=company,
        as_of_date=cutoff,
        top_k=requested_top_k,
    )

    assert len(results) == requested_top_k


def test_dense_retrieval_returns_no_results_when_nothing_is_eligible() -> None:
    chunks = _make_chunks()

    company = chunks[0].company

    earliest_date = min(
        chunk.publication_date for chunk in chunks if chunk.company == company
    )

    cutoff = earliest_date - timedelta(days=1)

    index = build_dense_index(chunks)

    results = retrieve_dense(
        index,
        query=chunks[0].text,
        company=company,
        as_of_date=cutoff,
        top_k=len(chunks),
    )

    assert results == []


def test_empty_corpus_cannot_build_dense_index() -> None:
    with pytest.raises(
        ValueError,
        match="Cannot build a dense index from an empty corpus.",
    ):
        build_dense_index([])


def test_non_positive_top_k_is_rejected() -> None:
    chunks = _make_chunks()
    index = build_dense_index(chunks)

    with pytest.raises(
        ValueError,
        match="top_k must be greater than 0.",
    ):
        retrieve_dense(
            index,
            query=chunks[0].text,
            company=chunks[0].company,
            as_of_date=max(chunk.publication_date for chunk in chunks),
            top_k=0,
        )
