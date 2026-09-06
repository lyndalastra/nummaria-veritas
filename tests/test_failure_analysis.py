from experiments.run_baseline import (
    BENCHMARK_PATH,
    build_invariance_baseline,
)
from nummaria_veritas.evaluation.benchmark import load_benchmark
from nummaria_veritas.evaluation.failure_analysis import (
    FailureDimension,
    analyse_failures,
    case_counts_by_perturbation_target,
    case_counts_by_perturbation_type,
    failure_counts_by_dimension,
    failure_counts_by_perturbation_target,
    failure_counts_by_perturbation_type,
    failure_signature_counts,
)
from nummaria_veritas.evaluation.metrics import evaluate_benchmark


def _get_baseline_case_evaluations():
    claims = load_benchmark(BENCHMARK_PATH)

    perturbations, verifications, deltas = build_invariance_baseline(claims)

    assert perturbations

    metrics = evaluate_benchmark(
        claims=perturbations,
        verifications_by_claim=verifications,
        deltas_by_claim=deltas,
    )

    return metrics.cases


def test_failure_analysis_preserves_every_baseline_case() -> None:
    evaluations = _get_baseline_case_evaluations()
    summary = analyse_failures(evaluations)

    assert evaluations
    assert len(summary.records) == len(evaluations)

    assert {record.claim_id for record in summary.records} == {
        evaluation.claim_id for evaluation in evaluations
    }


def test_failed_dimensions_match_evaluation_outcomes() -> None:
    evaluations = _get_baseline_case_evaluations()
    summary = analyse_failures(evaluations)

    records_by_claim_id = {record.claim_id: record for record in summary.records}

    for evaluation in evaluations:
        record = records_by_claim_id[evaluation.claim_id]

        expected_dimensions = tuple(
            dimension
            for dimension, matched in (
                (
                    FailureDimension.VERDICT,
                    evaluation.verdict_match,
                ),
                (
                    FailureDimension.CLAIM_ISSUES,
                    evaluation.claim_issues_match,
                ),
                (
                    FailureDimension.EVIDENCE_ISSUES,
                    evaluation.evidence_issues_match,
                ),
                (
                    FailureDimension.CORRECTION,
                    evaluation.correction_match,
                ),
            )
            if not matched
        )

        assert record.failed_dimensions == expected_dimensions


def test_failure_and_full_match_counts_partition_cases() -> None:
    evaluations = _get_baseline_case_evaluations()
    summary = analyse_failures(evaluations)

    assert summary.total_cases == len(evaluations)

    assert summary.failed_cases + summary.full_match_cases == summary.total_cases

    assert summary.failure_rate == (summary.failed_cases / summary.total_cases)

    assert summary.full_match_rate == (summary.full_match_cases / summary.total_cases)

    assert summary.failure_rate + summary.full_match_rate == 1.0


def test_failure_records_and_full_matches_are_consistent() -> None:
    evaluations = _get_baseline_case_evaluations()
    summary = analyse_failures(evaluations)

    assert summary.records

    for record in summary.records:
        assert record.is_failure == bool(record.failed_dimensions)

        assert record.is_full_match == (not record.failed_dimensions)

        assert record.is_failure != record.is_full_match


def test_grouped_failure_counts_are_derived_from_observed_cases() -> None:
    evaluations = _get_baseline_case_evaluations()
    summary = analyse_failures(evaluations)

    type_failures = failure_counts_by_perturbation_type(summary)
    type_totals = case_counts_by_perturbation_type(summary)

    target_failures = failure_counts_by_perturbation_target(summary)
    target_totals = case_counts_by_perturbation_target(summary)

    assert sum(type_totals.values()) == summary.total_cases
    assert sum(target_totals.values()) == summary.total_cases

    assert sum(type_failures.values()) == summary.failed_cases
    assert sum(target_failures.values()) == summary.failed_cases

    assert set(type_failures) <= set(type_totals)
    assert set(target_failures) <= set(target_totals)

    for group, failures in type_failures.items():
        assert failures <= type_totals[group]

    for group, failures in target_failures.items():
        assert failures <= target_totals[group]


def test_dimension_counts_equal_total_failed_dimensions() -> None:
    evaluations = _get_baseline_case_evaluations()
    summary = analyse_failures(evaluations)

    counts = failure_counts_by_dimension(summary)

    expected_total = sum(len(record.failed_dimensions) for record in summary.records)

    assert sum(counts.values()) == expected_total


def test_failure_signatures_partition_all_cases() -> None:
    evaluations = _get_baseline_case_evaluations()
    summary = analyse_failures(evaluations)

    signatures = failure_signature_counts(summary)

    assert sum(signatures.values()) == summary.total_cases

    assert set(signatures) == {record.failed_dimensions for record in summary.records}
