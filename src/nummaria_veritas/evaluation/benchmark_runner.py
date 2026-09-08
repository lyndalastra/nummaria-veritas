"""Resolve benchmark evidence interventions against the processed corpus."""

from nummaria_veritas.models import (
    BenchmarkClaim,
    EvidenceResult,
    IngestedChunk,
    PerturbationTarget,
)


def resolve_perturbed_evidence(
    *,
    claim: BenchmarkClaim,
    chunks: list[IngestedChunk],
) -> list[IngestedChunk] | None:
    if claim.perturbation_target != PerturbationTarget.EVIDENCE:
        return None

    chunks_by_id = {chunk.chunk_id: chunk for chunk in chunks}

    referenced_chunk_ids = [evidence.chunk_id for evidence in claim.perturbed_evidence]

    missing_chunk_ids = [
        chunk_id for chunk_id in referenced_chunk_ids if chunk_id not in chunks_by_id
    ]

    if missing_chunk_ids:
        missing_ids = ", ".join(missing_chunk_ids)

        raise ValueError(
            f"Perturbed evidence for claim {claim.claim_id!r} "
            f"references missing corpus chunks: {missing_ids}"
        )

    return [chunks_by_id[chunk_id] for chunk_id in referenced_chunk_ids]


def resolve_perturbed_evidence_results(
    *,
    claim: BenchmarkClaim,
    chunks: list[IngestedChunk],
) -> list[EvidenceResult] | None:
    resolved_chunks = resolve_perturbed_evidence(
        claim=claim,
        chunks=chunks,
    )

    if resolved_chunks is None:
        return None

    return [
        EvidenceResult(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            company=chunk.company,
            document_type=chunk.document_type,
            reporting_period=chunk.reporting_period,
            publication_date=chunk.publication_date,
            page_number=chunk.page_number,
            text=chunk.text,
            retrieval_score=None,
        )
        for chunk in resolved_chunks
    ]
