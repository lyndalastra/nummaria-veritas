from datetime import date

from nummaria_veritas.models import (
    AtomicClaim,
    Claim,
    IngestedChunk,
    PropositionType,
)
from nummaria_veritas.retrieval.dense import build_dense_index
from nummaria_veritas.retrieval.per_claim import (
    retrieve_evidence_for_atomic_claims,
)


def _make_chunks() -> list[IngestedChunk]:
    return [
        IngestedChunk(
            chunk_id=f"chunk_{index}",
            document_id=f"document_{index}",
            company="entity",
            document_type="test_document",
            reporting_period=f"period_{index}",
            publication_date=date.min,
            page_number=index + 1,
            chunk_index=index,
            text=f"financial evidence {index}",
        )
        for index in range(4)
    ]


def _make_claim() -> Claim:
    return Claim(
        claim_id="parent",
        company="entity",
        text="Composite claim.",
        as_of_date=date.min,
    )


def _make_atomic_claims(
    parent_claim_id: str,
) -> list[AtomicClaim]:
    return [
        AtomicClaim(
            atomic_claim_id=f"{parent_claim_id}_{index}",
            parent_claim_id=parent_claim_id,
            text=f"financial evidence {index}",
            proposition_type=PropositionType.FACT,
        )
        for index in range(2)
    ]


def test_retrieval_returns_one_result_set_per_atomic_claim() -> None:
    chunks = _make_chunks()
    claim = _make_claim()
    atomic_claims = _make_atomic_claims(claim.claim_id)

    index = build_dense_index(chunks)

    results = retrieve_evidence_for_atomic_claims(
        claim=claim,
        atomic_claims=atomic_claims,
        index=index,
    )

    assert len(results) == len(atomic_claims)


def test_atomic_claims_are_preserved_in_results() -> None:
    chunks = _make_chunks()
    claim = _make_claim()
    atomic_claims = _make_atomic_claims(claim.claim_id)

    index = build_dense_index(chunks)

    results = retrieve_evidence_for_atomic_claims(
        claim=claim,
        atomic_claims=atomic_claims,
        index=index,
    )

    returned_ids = [result.atomic_claim.atomic_claim_id for result in results]

    expected_ids = [atomic_claim.atomic_claim_id for atomic_claim in atomic_claims]

    assert returned_ids == expected_ids


def test_evidence_respects_parent_claim_time_and_company() -> None:
    chunks = _make_chunks()
    claim = _make_claim()
    atomic_claims = _make_atomic_claims(claim.claim_id)

    index = build_dense_index(chunks)

    results = retrieve_evidence_for_atomic_claims(
        claim=claim,
        atomic_claims=atomic_claims,
        index=index,
    )

    evidence = [item for result in results for item in result.evidence]

    assert all(item.company == claim.company for item in evidence)

    assert all(item.publication_date <= claim.as_of_date for item in evidence)
