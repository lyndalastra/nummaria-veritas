"""Chunk extracted pages while preserving document and page provenance."""

import re

from nummaria_veritas.models import Chunk, Page


def _split_into_blocks(text: str) -> list[str]:
    """Split page text on blank lines while preserving internal line structure."""
    return [block.strip() for block in re.split(r"\n\s*\n+", text) if block.strip()]


def _split_large_block(block: str, max_chars: int) -> list[str]:
    """Split an oversized block at line boundaries where possible."""
    if len(block) <= max_chars:
        return [block]

    lines = block.splitlines()
    pieces: list[str] = []
    current: list[str] = []
    current_length = 0

    for line in lines:
        line_length = len(line) + 1

        if current and current_length + line_length > max_chars:
            pieces.append("\n".join(current).strip())
            current = []
            current_length = 0

        current.append(line)
        current_length += line_length

    if current:
        pieces.append("\n".join(current).strip())

    return pieces


def chunk_page(
    page: Page,
    *,
    max_chars: int = 1800,
    overlap_chars: int = 250,
) -> list[Chunk]:
    if max_chars <= 0:
        raise ValueError("max_chars must be greater than 0.")

    if overlap_chars < 0:
        raise ValueError("overlap_chars must be non-negative.")

    if overlap_chars >= max_chars:
        raise ValueError("overlap_chars must be smaller than max_chars.")

    text = page.text.strip()

    if not text:
        return []

    raw_blocks = _split_into_blocks(text)

    blocks: list[str] = []
    for block in raw_blocks:
        blocks.extend(_split_large_block(block, max_chars))

    chunks: list[Chunk] = []
    current_blocks: list[str] = []
    current_length = 0
    chunk_index = 0

    for block in blocks:
        separator_length = 2 if current_blocks else 0
        proposed_length = current_length + separator_length + len(block)

        if current_blocks and proposed_length > max_chars:
            chunk_text = "\n\n".join(current_blocks)

            chunks.append(
                Chunk(
                    chunk_id=(f"{page.document_id}_p{page.page_number}_c{chunk_index}"),
                    document_id=page.document_id,
                    page_number=page.page_number,
                    chunk_index=chunk_index,
                    text=chunk_text,
                )
            )

            chunk_index += 1

            # Carry complete trailing blocks into the next chunk.
            overlap_blocks: list[str] = []
            overlap_length = 0

            for previous_block in reversed(current_blocks):
                additional_length = len(previous_block)
                if overlap_blocks:
                    additional_length += 2

                if (
                    overlap_blocks
                    and overlap_length + additional_length > overlap_chars
                ):
                    break

                overlap_blocks.insert(0, previous_block)
                overlap_length += additional_length

            current_blocks = overlap_blocks
            current_length = len("\n\n".join(current_blocks))

        if current_blocks:
            current_length += 2

        current_blocks.append(block)
        current_length += len(block)

    if current_blocks:
        chunks.append(
            Chunk(
                chunk_id=(f"{page.document_id}_p{page.page_number}_c{chunk_index}"),
                document_id=page.document_id,
                page_number=page.page_number,
                chunk_index=chunk_index,
                text="\n\n".join(current_blocks),
            )
        )

    return chunks


def chunk_pages(
    pages: list[Page],
    *,
    max_chars: int = 1800,
    overlap_chars: int = 250,
) -> list[Chunk]:
    chunks: list[Chunk] = []

    for page in pages:
        chunks.extend(
            chunk_page(
                page,
                max_chars=max_chars,
                overlap_chars=overlap_chars,
            )
        )

    return chunks
