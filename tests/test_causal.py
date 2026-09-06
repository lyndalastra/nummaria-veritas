from datetime import date

from nummaria_veritas.models import (
    AtomicClaim,
    ClaimIssue,
    EvidenceAssessment,
    EvidenceResult,
    EvidenceStance,
    PropositionType,
)
from nummaria_veritas.verification.causal import check_causal_overclaim


def _make_atomic_claim(
    *,
    is_causal: bool,
) -> AtomicClaim:
    return AtomicClaim(
        atomic_claim_id="atomic",
        parent_claim_id="parent",
        text="atomic_claim",
        proposition_type=PropositionType.INFERENCE,
        is_causal=is_causal,
    )


def _make_evidence() -> EvidenceResult:
    return EvidenceResult(
        chunk_id="chunk",
        document_id="document",
        company="entity",
        document_type="test_document",
        reporting_period="test_period",
        publication_date=date.min,
        page_number=1,
        text="evidence",
        retrieval_score=0.0,
    )


def test_non_causal_claim_is_not_flagged() -> None:
    atomic_claim = _make_atomic_claim(
        is_causal=False,
    )

    issues = check_causal_overclaim(
        atomic_claim=atomic_claim,
        assessments=[],
    )

    assert issues == []


def test_supported_causal_claim_is_not_flagged() -> None:
    atomic_claim = _make_atomic_claim(
        is_causal=True,
    )

    evidence = _make_evidence()

    assessments = [
        EvidenceAssessment(
            evidence=evidence,
            stance=EvidenceStance.SUPPORTS,
            explanation=(
                "The evidence supports the causal relationship "
                "asserted by the proposition."
            ),
        )
    ]

    issues = check_causal_overclaim(
        atomic_claim=atomic_claim,
        assessments=assessments,
    )

    assert issues == []


def test_unsupported_causal_claim_is_flagged() -> None:
    atomic_claim = _make_atomic_claim(
        is_causal=True,
    )

    evidence = _make_evidence()

    assessments = [
        EvidenceAssessment(
            evidence=evidence,
            stance=EvidenceStance.NEUTRAL,
            explanation=(
                "The evidence is relevant but does not establish "
                "the asserted causal relationship."
            ),
        )
    ]

    issues = check_causal_overclaim(
        atomic_claim=atomic_claim,
        assessments=assessments,
    )

    assert issues == [ClaimIssue.CAUSAL_OVERCLAIM]


def test_partial_claim_support_does_not_establish_causality() -> None:
    atomic_claim = _make_atomic_claim(
        is_causal=True,
    )

    evidence = _make_evidence()

    assessments = [
        EvidenceAssessment(
            evidence=evidence,
            stance=EvidenceStance.PARTIALLY_SUPPORTS,
            explanation=(
                "The evidence supports the underlying facts but does not "
                "establish the asserted causal relationship."
            ),
        )
    ]

    issues = check_causal_overclaim(
        atomic_claim=atomic_claim,
        assessments=assessments,
    )

    assert issues == [ClaimIssue.CAUSAL_OVERCLAIM]
