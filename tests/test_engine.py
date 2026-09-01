from datetime import date, timedelta

from nummaria_veritas.models import (
    AtomicClaim,
    Claim,
    ClaimIssue,
    EvidenceAssessment,
    EvidenceIssue,
    EvidenceResult,
    EvidenceStance,
    PropositionType,
    Verdict,
)
from nummaria_veritas.verification.engine import verify_atomic_claim


def _make_claim() -> Claim:
    return Claim(
        claim_id="parent",
        company="entity",
        text="claim",
        as_of_date=date.min + timedelta(days=1),
    )


def _make_atomic_claim(
    parent_claim_id: str,
) -> AtomicClaim:
    return AtomicClaim(
        atomic_claim_id=f"{parent_claim_id}_atomic",
        parent_claim_id=parent_claim_id,
        text="atomic_claim",
        proposition_type=PropositionType.FACT,
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
        text="evidence",
        retrieval_score=0.0,
    )


def test_supporting_evidence_produces_supported_verdict() -> None:
    claim = _make_claim()
    atomic_claim = _make_atomic_claim(claim.claim_id)

    evidence = _make_evidence(
        publication_date=claim.as_of_date,
    )

    assessments = [
        EvidenceAssessment(
            evidence=evidence,
            stance=EvidenceStance.SUPPORTS,
            explanation="The evidence supports the proposition.",
        )
    ]

    result = verify_atomic_claim(
        claim=claim,
        atomic_claim=atomic_claim,
        assessments=assessments,
    )

    assert result.verdict == Verdict.SUPPORTED
    assert result.supporting_evidence == [evidence]
    assert result.contradictory_evidence == []
    assert result.explanation


def test_contradictory_evidence_produces_contradicted_verdict() -> None:
    claim = _make_claim()
    atomic_claim = _make_atomic_claim(claim.claim_id)

    evidence = _make_evidence(
        publication_date=claim.as_of_date,
    )

    assessments = [
        EvidenceAssessment(
            evidence=evidence,
            stance=EvidenceStance.CONTRADICTS,
            explanation="The evidence contradicts the proposition.",
        )
    ]

    result = verify_atomic_claim(
        claim=claim,
        atomic_claim=atomic_claim,
        assessments=assessments,
    )

    assert result.verdict == Verdict.CONTRADICTED
    assert result.supporting_evidence == []
    assert result.contradictory_evidence == [evidence]
    assert result.explanation


def test_neutral_evidence_produces_unsupported_verdict() -> None:
    claim = _make_claim()
    atomic_claim = _make_atomic_claim(claim.claim_id)

    evidence = _make_evidence(
        publication_date=claim.as_of_date,
    )

    assessments = [
        EvidenceAssessment(
            evidence=evidence,
            stance=EvidenceStance.NEUTRAL,
            explanation=(
                "The evidence is relevant to the claim but does not "
                "support or contradict the proposition."
            ),
        )
    ]

    result = verify_atomic_claim(
        claim=claim,
        atomic_claim=atomic_claim,
        assessments=assessments,
    )

    assert result.verdict == Verdict.UNSUPPORTED
    assert result.supporting_evidence == []
    assert result.contradictory_evidence == []
    assert result.explanation


def test_no_evidence_produces_insufficient_evidence_verdict() -> None:
    claim = _make_claim()
    atomic_claim = _make_atomic_claim(claim.claim_id)

    result = verify_atomic_claim(
        claim=claim,
        atomic_claim=atomic_claim,
        assessments=[],
    )

    assert result.verdict == Verdict.INSUFFICIENT_EVIDENCE
    assert result.supporting_evidence == []
    assert result.contradictory_evidence == []
    assert result.explanation
    assert "evidence" in result.explanation.lower()


def test_future_supporting_evidence_is_flagged_as_temporal_leakage() -> None:
    claim = _make_claim()
    atomic_claim = _make_atomic_claim(claim.claim_id)

    evidence = _make_evidence(
        publication_date=claim.as_of_date + timedelta(days=1),
    )

    assessments = [
        EvidenceAssessment(
            evidence=evidence,
            stance=EvidenceStance.SUPPORTS,
            explanation=(
                "The evidence supports the proposition on its content, "
                "but it was published after the claim's as-of date."
            ),
        )
    ]

    result = verify_atomic_claim(
        claim=claim,
        atomic_claim=atomic_claim,
        assessments=assessments,
    )

    assert EvidenceIssue.TEMPORAL_LEAKAGE in result.evidence_issues

    # Semantically supportive but temporally inadmissible evidence
    # must not establish a supported verdict.
    assert result.verdict != Verdict.SUPPORTED


def test_unsupported_causal_inference_is_flagged_by_engine() -> None:
    claim = _make_claim()

    atomic_claim = AtomicClaim(
        atomic_claim_id=f"{claim.claim_id}_atomic",
        parent_claim_id=claim.claim_id,
        text="atomic_claim",
        proposition_type=PropositionType.INFERENCE,
        is_causal=True,
    )

    evidence = _make_evidence(
        publication_date=claim.as_of_date,
    )

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

    result = verify_atomic_claim(
        claim=claim,
        atomic_claim=atomic_claim,
        assessments=assessments,
    )

    assert ClaimIssue.CAUSAL_OVERCLAIM in result.claim_issues
    assert result.verdict != Verdict.SUPPORTED
