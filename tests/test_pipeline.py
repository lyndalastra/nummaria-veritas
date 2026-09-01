from pathlib import Path

from nummaria_veritas.ingestion.manifest import load_document_manifest
from nummaria_veritas.ingestion.pipeline import ingest_corpus, ingest_document

MANIFEST_PATH = Path("configs/documents.yaml")


def test_ingested_chunks_preserve_document_metadata() -> None:
    document = load_document_manifest(MANIFEST_PATH)[0]

    chunks = ingest_document(document)

    assert chunks
    assert all(chunk.document_id == document.document_id for chunk in chunks)
    assert all(chunk.company == document.company for chunk in chunks)
    assert all(chunk.document_type == document.document_type for chunk in chunks)
    assert all(chunk.reporting_period == document.reporting_period for chunk in chunks)
    assert all(chunk.publication_date == document.publication_date for chunk in chunks)


def test_ingested_chunk_ids_are_unique_within_document() -> None:
    document = load_document_manifest(MANIFEST_PATH)[0]

    chunks = ingest_document(document)

    chunk_ids = [chunk.chunk_id for chunk in chunks]

    assert len(chunk_ids) == len(set(chunk_ids))


def test_corpus_preserves_manifest_provenance() -> None:
    documents = load_document_manifest(MANIFEST_PATH)
    chunks = ingest_corpus(documents)

    documents_by_id = {document.document_id: document for document in documents}

    for chunk in chunks:
        document = documents_by_id[chunk.document_id]

        assert chunk.company == document.company
        assert chunk.document_type == document.document_type
        assert chunk.reporting_period == document.reporting_period
        assert chunk.publication_date == document.publication_date


def test_chunk_ids_are_globally_unique() -> None:
    documents = load_document_manifest(MANIFEST_PATH)
    chunks = ingest_corpus(documents)

    chunk_ids = [chunk.chunk_id for chunk in chunks]

    assert len(chunk_ids) == len(set(chunk_ids))
