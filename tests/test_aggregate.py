import pytest

from nummaria_veritas.models import (
    AtomicVerificationResult,
    ClaimIssue,
    EvidenceIssue,
    Verdict,
)
from nummaria_veritas.verification.aggregate import (
    aggregate_claim_verification,
)


def _make_atomic_result(
    *,
    atomic_claim_id: str,
    verdict: Verdict,
    claim_issues: list[ClaimIssue] | None = None,
    evidence_issues: list[EvidenceIssue] | None = None,
) -> AtomicVerificationResult:
    return AtomicVerificationResult(
        atomic_claim_id=atomic_claim_id,
        verdict=verdict,
        claim_issues=claim_issues or [],
        evidence_issues=evidence_issues or [],
        supporting_evidence=[],
        contradictory_evidence=[],
        explanation="result",
    )


@pytest.mark.parametrize(
    ("atomic_verdicts", "expected_parent_verdict"),
    [
        (
            [Verdict.SUPPORTED_CLAIM],
            Verdict.SUPPORTED_CLAIM,
        ),
        (
            [
                Verdict.SUPPORTED_CLAIM,
                Verdict.SUPPORTED_CLAIM,
            ],
            Verdict.SUPPORTED_CLAIM,
        ),
        (
            [Verdict.CONTRADICTED_CLAIM],
            Verdict.CONTRADICTED_CLAIM,
        ),
        (
            [
                Verdict.CONTRADICTED_CLAIM,
                Verdict.CONTRADICTED_CLAIM,
            ],
            Verdict.CONTRADICTED_CLAIM,
        ),
        (
            [
                Verdict.SUPPORTED_CLAIM,
                Verdict.CONTRADICTED_CLAIM,
            ],
            Verdict.PARTIALLY_SUPPORTED_CLAIM,
        ),
        (
            [
                Verdict.SUPPORTED_CLAIM,
                Verdict.INSUFFICIENT_EVIDENCE,
            ],
            Verdict.PARTIALLY_SUPPORTED_CLAIM,
        ),
        (
            [Verdict.UNSUPPORTED_CLAIM],
            Verdict.UNSUPPORTED_CLAIM,
        ),
        (
            [Verdict.INVALID_EVIDENCE],
            Verdict.INVALID_EVIDENCE,
        ),
        (
            [
                Verdict.INVALID_EVIDENCE,
                Verdict.INVALID_EVIDENCE,
            ],
            Verdict.INVALID_EVIDENCE,
        ),
        (
            [Verdict.INSUFFICIENT_EVIDENCE],
            Verdict.INSUFFICIENT_EVIDENCE,
        ),
    ],
)
def test_parent_verdict_is_derived_from_atomic_verdicts(
    atomic_verdicts: list[Verdict],
    expected_parent_verdict: Verdict,
) -> None:
    atomic_results = [
        _make_atomic_result(
            atomic_claim_id=f"atomic_{index}",
            verdict=verdict,
        )
        for index, verdict in enumerate(atomic_verdicts)
    ]

    result = aggregate_claim_verification(
        claim_id="parent",
        atomic_results=atomic_results,
    )

    assert result.verdict == expected_parent_verdict


def test_parent_aggregates_claim_issues_without_duplicates() -> None:
    atomic_results = [
        _make_atomic_result(
            atomic_claim_id="atomic_a",
            verdict=Verdict.PARTIALLY_SUPPORTED_CLAIM,
            claim_issues=[
                ClaimIssue.CAUSAL_OVERCLAIM,
            ],
        ),
        _make_atomic_result(
            atomic_claim_id="atomic_b",
            verdict=Verdict.PARTIALLY_SUPPORTED_CLAIM,
            claim_issues=[
                ClaimIssue.CAUSAL_OVERCLAIM,
                ClaimIssue.NUMERICAL_INCONSISTENCY,
            ],
        ),
    ]

    result = aggregate_claim_verification(
        claim_id="parent",
        atomic_results=atomic_results,
    )

    assert result.claim_issues == [
        ClaimIssue.CAUSAL_OVERCLAIM,
        ClaimIssue.NUMERICAL_INCONSISTENCY,
    ]


def test_parent_aggregates_evidence_issues_without_duplicates() -> None:
    atomic_results = [
        _make_atomic_result(
            atomic_claim_id="atomic_a",
            verdict=Verdict.INSUFFICIENT_EVIDENCE,
            evidence_issues=[
                EvidenceIssue.TEMPORAL_LEAKAGE,
            ],
        ),
        _make_atomic_result(
            atomic_claim_id="atomic_b",
            verdict=Verdict.INSUFFICIENT_EVIDENCE,
            evidence_issues=[
                EvidenceIssue.TEMPORAL_LEAKAGE,
            ],
        ),
    ]

    result = aggregate_claim_verification(
        claim_id="parent",
        atomic_results=atomic_results,
    )

    assert result.evidence_issues == [
        EvidenceIssue.TEMPORAL_LEAKAGE,
    ]


def test_empty_atomic_results_produce_insufficient_evidence() -> None:
    result = aggregate_claim_verification(
        claim_id="parent",
        atomic_results=[],
    )

    assert result.verdict == Verdict.INSUFFICIENT_EVIDENCE
    assert result.atomic_results == []
    assert result.explanation
