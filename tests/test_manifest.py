from pathlib import Path

from nummaria_veritas.ingestion.manifest import load_document_manifest

MANIFEST_PATH = Path("configs/documents.yaml")


def test_manifest_is_not_empty() -> None:
    documents = load_document_manifest(MANIFEST_PATH)

    assert documents


def test_document_ids_are_unique() -> None:
    documents = load_document_manifest(MANIFEST_PATH)

    document_ids = [document.document_id for document in documents]

    assert len(document_ids) == len(set(document_ids))


def test_all_source_paths_exist() -> None:
    documents = load_document_manifest(MANIFEST_PATH)

    missing_paths = [
        document.source_path
        for document in documents
        if not Path(document.source_path).exists()
    ]

    assert not missing_paths, f"Missing source files: {missing_paths}"


def test_all_documents_have_publication_dates() -> None:
    documents = load_document_manifest(MANIFEST_PATH)

    assert all(document.publication_date for document in documents)
