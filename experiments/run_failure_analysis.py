"""Run failure analysis over perturbation-invariance baseline results."""

from collections import Counter
from collections.abc import Hashable

from experiments.run_baseline import (
    BENCHMARK_PATH,
    build_invariance_baseline,
)
from nummaria_veritas.evaluation.benchmark import load_benchmark
from nummaria_veritas.evaluation.failure_analysis import (
    FailureDimension,
    FailureSummary,
    analyse_failures,
    case_counts_by_perturbation_target,
    case_counts_by_perturbation_type,
    failure_counts_by_dimension,
    failure_counts_by_perturbation_target,
    failure_counts_by_perturbation_type,
    failure_signature_counts,
)
from nummaria_veritas.evaluation.metrics import evaluate_benchmark


def run_failure_analysis() -> FailureSummary:
    claims = load_benchmark(BENCHMARK_PATH)

    perturbations, verifications, deltas = build_invariance_baseline(claims)

    if not perturbations:
        raise ValueError("The benchmark contains no perturbation cases.")

    metrics = evaluate_benchmark(
        claims=perturbations,
        verifications_by_claim=verifications,
        deltas_by_claim=deltas,
    )

    return analyse_failures(metrics.cases)


def _format_percentage(value: float) -> str:
    return f"{value:.1%}"


def _format_group(group: object) -> str:
    value = getattr(group, "value", None)

    if value is not None:
        return str(value)

    if group is None:
        return "none"

    return str(group)


def _format_dimensions(
    dimensions: tuple[FailureDimension, ...],
) -> str:
    if not dimensions:
        return "none / full match"

    return ", ".join(dimension.value for dimension in dimensions)


def _print_grouped_counts(
    *,
    failures: Counter[Hashable],
    totals: Counter[Hashable],
) -> None:
    for group, total in totals.items():
        failed = failures[group]

        print(
            f"{_format_group(group):<28}"
            f"{failed:>4} / {total:<4}"
            f"{_format_percentage(failed / total):>12}"
        )


def print_failure_analysis(
    summary: FailureSummary,
) -> None:
    print()
    print("=" * 72)
    print("NUMMARIA VERITAS — FAILURE ANALYSIS")
    print("=" * 72)
    print()

    print("Overall")
    print(f"  Cases:              {summary.total_cases}")
    print(f"  Failed cases:       {summary.failed_cases}")
    print(f"  Full-match cases:   {summary.full_match_cases}")
    print(f"  Failure rate:       {_format_percentage(summary.failure_rate)}")
    print(f"  Full-match rate:    {_format_percentage(summary.full_match_rate)}")

    print()
    print("Failures by evaluation dimension")
    print("-" * 72)

    dimension_counts = failure_counts_by_dimension(summary)

    for dimension, count in dimension_counts.items():
        print(f"{dimension.value:<28}{count:>8}")

    print()
    print("Failures by perturbation type")
    print("-" * 72)

    _print_grouped_counts(
        failures=failure_counts_by_perturbation_type(summary),
        totals=case_counts_by_perturbation_type(summary),
    )

    print()
    print("Failures by perturbation target")
    print("-" * 72)

    _print_grouped_counts(
        failures=failure_counts_by_perturbation_target(summary),
        totals=case_counts_by_perturbation_target(summary),
    )

    print()
    print("Failure signatures")
    print("-" * 72)

    for signature, count in failure_signature_counts(summary).items():
        print(f"{_format_dimensions(signature):<52}{count:>4}")

    print()
    print("Case-level failure signatures")
    print("-" * 72)

    for record in summary.records:
        if record.is_failure:
            print(
                f"{record.claim_id:<32}{_format_dimensions(record.failed_dimensions)}"
            )

    full_matches = tuple(record for record in summary.records if record.is_full_match)

    if full_matches:
        print()
        print("Full-match cases")
        print("-" * 72)

        for record in full_matches:
            print(
                f"{record.claim_id:<32}"
                f"{record.perturbation_type} / "
                f"{_format_group(record.perturbation_target)}"
            )


def main() -> None:
    summary = run_failure_analysis()
    print_failure_analysis(summary)


if __name__ == "__main__":
    main()
