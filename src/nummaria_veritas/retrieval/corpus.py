"""Load and filter the processed evidence corpus by point-in-time eligibility."""

import json
from datetime import date
from pathlib import Path

from nummaria_veritas.models import IngestedChunk


def load_chunks(path: str | Path) -> list[IngestedChunk]:
    chunk_path = Path(path)

    chunks: list[IngestedChunk] = []

    with chunk_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                data = json.loads(line)
                chunk = IngestedChunk.model_validate(data)
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(f"Invalid chunk at line {line_number}: {exc}") from exc

            chunks.append(chunk)

    return chunks


def filter_chunks_as_of(
    chunks: list[IngestedChunk],
    *,
    company: str,
    as_of_date: date,
) -> list[IngestedChunk]:
    return [
        chunk
        for chunk in chunks
        if chunk.company == company and chunk.publication_date <= as_of_date
    ]
