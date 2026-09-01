from datetime import date

from nummaria_veritas.decomposition.static import StaticClaimDecomposer
from nummaria_veritas.models import (
    AtomicClaim,
    Claim,
    ClaimDecomposition,
    IngestedChunk,
    PropositionType,
)
from nummaria_veritas.retrieval.dense import build_dense_index
from nummaria_veritas.retrieval.pipeline import retrieve_evidence_for_claim


def test_claim_retrieval_pipeline_preserves_structure() -> None:
    claim = Claim(
        claim_id="parent",
        company="entity",
        text="Composite statement.",
        as_of_date=date.min,
    )

    atomic_claims = [
        AtomicClaim(
            atomic_claim_id=f"{claim.claim_id}_{index}",
            parent_claim_id=claim.claim_id,
            text=f"financial proposition about metric {index}",
            proposition_type=PropositionType.FACT,
        )
        for index in range(3)
    ]

    decomposition = ClaimDecomposition(
        parent_claim_id=claim.claim_id,
        atomic_claims=atomic_claims,
    )

    decomposer = StaticClaimDecomposer({claim.claim_id: decomposition})

    chunks = [
        IngestedChunk(
            chunk_id=f"chunk_{index}",
            document_id=f"document_{index}",
            company=claim.company,
            document_type="test_document",
            reporting_period=f"period_{index}",
            publication_date=claim.as_of_date,
            page_number=index + 1,
            chunk_index=index,
            text=(
                f"financial evidence for metric {index} "
                f"with distinct supporting context {index}"
            ),
        )
        for index in range(len(atomic_claims))
    ]

    index = build_dense_index(chunks)

    result = retrieve_evidence_for_claim(
        claim=claim,
        decomposer=decomposer,
        index=index,
    )

    assert result.claim == claim
    assert result.decomposition == decomposition
    assert len(result.atomic_evidence) == len(atomic_claims)

    returned_ids = [
        bundle.atomic_claim.atomic_claim_id for bundle in result.atomic_evidence
    ]

    expected_ids = [atomic_claim.atomic_claim_id for atomic_claim in atomic_claims]

    assert returned_ids == expected_ids

    assert all(bundle.evidence for bundle in result.atomic_evidence)

    assert all(
        evidence.company == claim.company
        for bundle in result.atomic_evidence
        for evidence in bundle.evidence
    )

    assert all(
        evidence.publication_date <= claim.as_of_date
        for bundle in result.atomic_evidence
        for evidence in bundle.evidence
    )
