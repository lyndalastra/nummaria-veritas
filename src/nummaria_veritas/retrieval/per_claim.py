"""Retrieve evidence for already-decomposed atomic claims."""

from dataclasses import dataclass

from nummaria_veritas.models import AtomicClaim, Claim, EvidenceResult
from nummaria_veritas.retrieval.dense import DenseIndex, retrieve_dense


@dataclass
class AtomicEvidence:
    atomic_claim: AtomicClaim
    evidence: list[EvidenceResult]


def retrieve_evidence_for_atomic_claims(
    *,
    claim: Claim,
    atomic_claims: list[AtomicClaim],
    index: DenseIndex,
    top_k: int = 5,
) -> list[AtomicEvidence]:
    return [
        AtomicEvidence(
            atomic_claim=atomic_claim,
            evidence=retrieve_dense(
                index,
                query=atomic_claim.text,
                company=claim.company,
                as_of_date=claim.as_of_date,
                top_k=top_k,
            ),
        )
        for atomic_claim in atomic_claims
    ]
