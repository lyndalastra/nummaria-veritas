from datetime import date, timedelta

from nummaria_veritas.models import (
    Claim,
    EvidenceIssue,
    EvidenceResult,
)
from nummaria_veritas.verification.temporal import check_temporal_validity


def _make_claim() -> Claim:
    return Claim(
        claim_id="claim",
        company="entity",
        text="Test claim.",
        as_of_date=date.min + timedelta(days=10),
    )


def _make_evidence(
    *,
    publication_date: date,
) -> EvidenceResult:
    return EvidenceResult(
        chunk_id="chunk",
        document_id="document",
        company="entity",
        document_type="test_document",
        reporting_period="test_period",
        publication_date=publication_date,
        page_number=1,
        text="Test evidence.",
        retrieval_score=0.0,
    )


def test_temporal_check_passes_when_all_evidence_is_available() -> None:
    claim = _make_claim()

    evidence = [
        _make_evidence(
            publication_date=claim.as_of_date,
        )
    ]

    issues = check_temporal_validity(
        claim=claim,
        evidence=evidence,
    )

    assert issues == []


def test_temporal_check_detects_future_evidence() -> None:
    claim = _make_claim()

    evidence = [
        _make_evidence(
            publication_date=claim.as_of_date + timedelta(days=1),
        )
    ]

    issues = check_temporal_validity(
        claim=claim,
        evidence=evidence,
    )

    assert issues == [EvidenceIssue.TEMPORAL_LEAKAGE]


def test_temporal_check_flags_mixed_evidence_if_any_item_is_future() -> None:
    claim = _make_claim()

    evidence = [
        _make_evidence(
            publication_date=claim.as_of_date,
        ),
        _make_evidence(
            publication_date=claim.as_of_date + timedelta(days=1),
        ),
    ]

    issues = check_temporal_validity(
        claim=claim,
        evidence=evidence,
    )

    assert issues == [EvidenceIssue.TEMPORAL_LEAKAGE]
