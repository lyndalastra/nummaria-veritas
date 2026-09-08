"""Load and validate the financial document manifest."""

from pathlib import Path

import yaml
from pydantic import ValidationError

from nummaria_veritas.models import Document


def load_document_manifest(path: str | Path) -> list[Document]:
    manifest_path = Path(path)

    with manifest_path.open("r", encoding="utf-8") as file:
        raw_manifest = yaml.safe_load(file)

    if not isinstance(raw_manifest, dict):
        raise TypeError("Document manifest must be a mapping.")

    raw_documents = raw_manifest.get("documents")

    if not isinstance(raw_documents, list):
        raise TypeError("Document manifest must contain a 'documents' list.")

    documents: list[Document] = []

    for index, raw_document in enumerate(raw_documents, start=1):
        try:
            document = Document.model_validate(raw_document)
        except ValidationError as exc:
            raise ValueError(
                f"Invalid document entry at position {index}: {exc}"
            ) from exc

        documents.append(document)

    return documents
