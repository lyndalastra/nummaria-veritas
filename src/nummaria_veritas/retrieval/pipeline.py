"""Coordinate claim decomposition and point-in-time evidence retrieval."""

from nummaria_veritas.decomposition.base import ClaimDecomposer
from nummaria_veritas.models import (
    AtomicEvidenceBundle,
    Claim,
    ClaimEvidenceBundle,
)
from nummaria_veritas.retrieval.dense import DenseIndex, retrieve_dense


def retrieve_evidence_for_claim(
    *,
    claim: Claim,
    decomposer: ClaimDecomposer,
    index: DenseIndex,
    top_k: int = 5,
) -> ClaimEvidenceBundle:
    """Decompose a claim and retrieve point-in-time evidence for each proposition."""

    decomposition = decomposer.decompose(claim)

    atomic_evidence = [
        AtomicEvidenceBundle(
            atomic_claim=atomic_claim,
            evidence=retrieve_dense(
                index,
                query=atomic_claim.text,
                company=claim.company,
                as_of_date=claim.as_of_date,
                top_k=top_k,
            ),
        )
        for atomic_claim in decomposition.atomic_claims
    ]

    return ClaimEvidenceBundle(
        claim=claim,
        decomposition=decomposition,
        atomic_evidence=atomic_evidence,
    )
