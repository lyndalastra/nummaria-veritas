"""Build the processed evidence corpus from manifest documents."""

import json
from pathlib import Path

from nummaria_veritas.ingestion.chunking import chunk_pages
from nummaria_veritas.ingestion.pdf import extract_pages
from nummaria_veritas.models import Document, IngestedChunk


def ingest_document(
    document: Document,
    *,
    max_chars: int = 1800,
    overlap_chars: int = 250,
) -> list[IngestedChunk]:
    pages = extract_pages(document)

    chunks = chunk_pages(
        pages,
        max_chars=max_chars,
        overlap_chars=overlap_chars,
    )

    return [
        IngestedChunk(
            chunk_id=chunk.chunk_id,
            document_id=document.document_id,
            company=document.company,
            document_type=document.document_type,
            reporting_period=document.reporting_period,
            publication_date=document.publication_date,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
            text=chunk.text,
        )
        for chunk in chunks
    ]


def write_chunks_jsonl(
    chunks: list[IngestedChunk],
    output_path: str | Path,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(
                json.dumps(
                    chunk.model_dump(mode="json"),
                    ensure_ascii=False,
                )
            )
            file.write("\n")


def ingest_corpus(
    documents: list[Document],
    *,
    max_chars: int = 1800,
    overlap_chars: int = 250,
) -> list[IngestedChunk]:
    all_chunks: list[IngestedChunk] = []

    for document in documents:
        all_chunks.extend(
            ingest_document(
                document,
                max_chars=max_chars,
                overlap_chars=overlap_chars,
            )
        )

    return all_chunks
