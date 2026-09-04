from pathlib import Path

import pytest

from experiments.run_baseline import (
    build_invariance_baseline,
)
from nummaria_veritas.evaluation.benchmark import load_benchmark
from nummaria_veritas.evaluation.metrics import evaluate_benchmark
from nummaria_veritas.models import (
    PerturbationType,
)

BENCHMARK_PATH = Path("data/benchmark/claims.jsonl")


def test_invariance_baseline_only_includes_perturbations() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    perturbations, verifications, deltas = build_invariance_baseline(claims)

    expected_claim_ids = {
        claim.claim_id
        for claim in claims
        if claim.perturbation_type != PerturbationType.NONE
    }

    assert {claim.claim_id for claim in perturbations} == expected_claim_ids

    assert set(verifications) == expected_claim_ids
    assert set(deltas) == expected_claim_ids


def test_invariance_baseline_inherits_source_verification_state() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    claims_by_id = {claim.claim_id: claim for claim in claims}

    perturbations, verifications, _ = build_invariance_baseline(claims)

    for claim in perturbations:
        assert claim.source_claim_id is not None

        source_claim = claims_by_id[claim.source_claim_id]
        verification = verifications[claim.claim_id]

        assert verification.verdict == source_claim.expected_verdict
        assert verification.claim_issues == source_claim.expected_claim_issues
        assert verification.evidence_issues == source_claim.expected_evidence_issues


def test_invariance_baseline_inherits_source_correction_state() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    claims_by_id = {claim.claim_id: claim for claim in claims}

    perturbations, _, deltas = build_invariance_baseline(claims)

    for claim in perturbations:
        assert claim.source_claim_id is not None

        source_claim = claims_by_id[claim.source_claim_id]
        delta = deltas[claim.claim_id]

        if source_claim.expected_revised_claim is None:
            assert delta is None
        else:
            assert delta is not None
            assert delta.original_claim == claim.text
            assert delta.revised_claim == source_claim.expected_revised_claim


def test_invariance_baseline_can_be_scored() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    perturbations, verifications, deltas = build_invariance_baseline(claims)

    metrics = evaluate_benchmark(
        claims=perturbations,
        verifications_by_claim=verifications,
        deltas_by_claim=deltas,
    )

    assert metrics.overall.total_cases == len(perturbations)


def test_invariance_baseline_rejects_missing_source_claim_id() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    perturbation = next(
        claim for claim in claims if claim.perturbation_type != PerturbationType.NONE
    )

    invalid_claim = perturbation.model_copy(
        update={
            "source_claim_id": None,
        }
    )

    modified_claims = [
        invalid_claim if claim.claim_id == perturbation.claim_id else claim
        for claim in claims
    ]

    with pytest.raises(
        ValueError,
        match=perturbation.claim_id,
    ):
        build_invariance_baseline(modified_claims)


def test_invariance_baseline_rejects_missing_source_claim() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    perturbation = next(
        claim for claim in claims if claim.perturbation_type != PerturbationType.NONE
    )

    assert perturbation.source_claim_id is not None

    claims_without_source = [
        claim for claim in claims if claim.claim_id != perturbation.source_claim_id
    ]

    with pytest.raises(
        ValueError,
        match=perturbation.source_claim_id,
    ):
        build_invariance_baseline(claims_without_source)
