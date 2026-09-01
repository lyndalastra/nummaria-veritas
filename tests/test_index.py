from pathlib import Path

import pytest

from nummaria_veritas.retrieval.corpus import load_chunks
from nummaria_veritas.retrieval.index import build_lexical_index

CHUNKS_PATH = Path("data/processed/chunks.jsonl")


def test_index_contains_all_chunks() -> None:
    chunks = load_chunks(CHUNKS_PATH)

    index = build_lexical_index(chunks)

    assert index.matrix.shape[0] == len(chunks)
    assert len(index.chunks) == len(chunks)


def test_index_has_non_empty_vocabulary() -> None:
    chunks = load_chunks(CHUNKS_PATH)

    index = build_lexical_index(chunks)

    assert index.vectorizer.vocabulary_


def test_index_has_features() -> None:
    chunks = load_chunks(CHUNKS_PATH)

    index = build_lexical_index(chunks)

    assert index.matrix.shape[1] > 0


def test_index_preserves_chunk_order() -> None:
    chunks = load_chunks(CHUNKS_PATH)

    index = build_lexical_index(chunks)

    original_ids = [chunk.chunk_id for chunk in chunks]
    indexed_ids = [chunk.chunk_id for chunk in index.chunks]

    assert indexed_ids == original_ids


def test_empty_corpus_cannot_be_indexed() -> None:
    with pytest.raises(
        ValueError,
        match="Cannot build an index from an empty corpus.",
    ):
        build_lexical_index([])
