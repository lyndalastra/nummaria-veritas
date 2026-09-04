from pathlib import Path

import pytest

from nummaria_veritas.evaluation.benchmark import load_benchmark
from nummaria_veritas.evaluation.metrics import (
    evaluate_benchmark,
    get_benchmark_failures,
)
from nummaria_veritas.models import (
    ClaimDelta,
    ClaimVerification,
    Verdict,
)

BENCHMARK_PATH = Path("data/benchmark/claims.jsonl")


def _gold_verifications() -> dict[str, ClaimVerification]:
    claims = load_benchmark(BENCHMARK_PATH)

    return {
        claim.claim_id: ClaimVerification(
            claim_id=claim.claim_id,
            atomic_results=[],
            verdict=claim.expected_verdict,
            claim_issues=list(claim.expected_claim_issues),
            evidence_issues=list(claim.expected_evidence_issues),
            explanation="Matches benchmark gold.",
        )
        for claim in claims
    }


def _gold_deltas() -> dict[str, ClaimDelta | None]:
    claims = load_benchmark(BENCHMARK_PATH)

    return {
        claim.claim_id: (
            ClaimDelta(
                original_claim=claim.text,
                revised_claim=claim.expected_revised_claim,
                changes=[],
            )
            if claim.expected_revised_claim is not None
            else None
        )
        for claim in claims
    }


def test_gold_results_produce_perfect_metrics() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    metrics = evaluate_benchmark(
        claims=claims,
        verifications_by_claim=_gold_verifications(),
        deltas_by_claim=_gold_deltas(),
    )

    assert metrics.overall.total_cases == len(claims)
    assert metrics.overall.verdict_accuracy == 1.0
    assert metrics.overall.claim_issue_exact_match == 1.0
    assert metrics.overall.evidence_issue_exact_match == 1.0
    assert metrics.overall.correction_exact_match == 1.0
    assert metrics.overall.case_exact_match == 1.0

    assert get_benchmark_failures(metrics) == ()


def test_verdict_failure_is_detected_from_benchmark_case() -> None:
    claims = load_benchmark(BENCHMARK_PATH)
    verifications = _gold_verifications()

    claim = claims[0]

    different_verdict = next(
        verdict for verdict in Verdict if verdict != claim.expected_verdict
    )

    verifications[claim.claim_id] = verifications[claim.claim_id].model_copy(
        update={
            "verdict": different_verdict,
        }
    )

    metrics = evaluate_benchmark(
        claims=claims,
        verifications_by_claim=verifications,
        deltas_by_claim=_gold_deltas(),
    )

    failures = get_benchmark_failures(metrics)

    assert {failure.claim_id for failure in failures} == {claim.claim_id}

    assert failures[0].failed_dimensions == ("verdict",)


def test_claim_issue_failure_is_detected_from_labelled_case() -> None:
    claims = load_benchmark(BENCHMARK_PATH)
    verifications = _gold_verifications()

    claim = next(claim for claim in claims if claim.expected_claim_issues)

    verifications[claim.claim_id] = verifications[claim.claim_id].model_copy(
        update={
            "claim_issues": [],
        }
    )

    metrics = evaluate_benchmark(
        claims=claims,
        verifications_by_claim=verifications,
        deltas_by_claim=_gold_deltas(),
    )

    failure = next(
        failure
        for failure in get_benchmark_failures(metrics)
        if failure.claim_id == claim.claim_id
    )

    assert "claim_issues" in failure.failed_dimensions


def test_evidence_issue_failure_is_detected_from_labelled_case() -> None:
    claims = load_benchmark(BENCHMARK_PATH)
    verifications = _gold_verifications()

    claim = next(claim for claim in claims if claim.expected_evidence_issues)

    verifications[claim.claim_id] = verifications[claim.claim_id].model_copy(
        update={
            "evidence_issues": [],
        }
    )

    metrics = evaluate_benchmark(
        claims=claims,
        verifications_by_claim=verifications,
        deltas_by_claim=_gold_deltas(),
    )

    failure = next(
        failure
        for failure in get_benchmark_failures(metrics)
        if failure.claim_id == claim.claim_id
    )

    assert "evidence_issues" in failure.failed_dimensions


def test_correction_failure_is_detected_from_expected_revision() -> None:
    claims = load_benchmark(BENCHMARK_PATH)
    deltas = _gold_deltas()

    claim = next(claim for claim in claims if claim.expected_revised_claim is not None)

    deltas[claim.claim_id] = None

    metrics = evaluate_benchmark(
        claims=claims,
        verifications_by_claim=_gold_verifications(),
        deltas_by_claim=deltas,
    )

    failure = next(
        failure
        for failure in get_benchmark_failures(metrics)
        if failure.claim_id == claim.claim_id
    )

    assert "correction" in failure.failed_dimensions


def test_metrics_are_broken_down_by_existing_perturbation_metadata() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    metrics = evaluate_benchmark(
        claims=claims,
        verifications_by_claim=_gold_verifications(),
        deltas_by_claim=_gold_deltas(),
    )

    expected_types = {claim.perturbation_type.value for claim in claims}

    expected_targets = {
        (
            claim.perturbation_target.value
            if claim.perturbation_target is not None
            else "none"
        )
        for claim in claims
    }

    assert set(metrics.by_perturbation_type) == expected_types
    assert set(metrics.by_perturbation_target) == expected_targets

    assert sum(
        summary.total_cases for summary in metrics.by_perturbation_type.values()
    ) == len(claims)

    assert sum(
        summary.total_cases for summary in metrics.by_perturbation_target.values()
    ) == len(claims)


def test_missing_verification_results_are_rejected() -> None:
    claims = load_benchmark(BENCHMARK_PATH)
    verifications = _gold_verifications()

    removed_claim = claims[0]

    del verifications[removed_claim.claim_id]

    with pytest.raises(
        ValueError,
        match=removed_claim.claim_id,
    ):
        evaluate_benchmark(
            claims=claims,
            verifications_by_claim=verifications,
            deltas_by_claim=_gold_deltas(),
        )
