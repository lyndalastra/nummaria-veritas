"""Run the perturbation-invariance baseline experiment."""

from pathlib import Path

from nummaria_veritas.evaluation.benchmark import load_benchmark
from nummaria_veritas.evaluation.metrics import (
    BenchmarkMetrics,
    MetricSummary,
    evaluate_benchmark,
    get_benchmark_failures,
)
from nummaria_veritas.models import (
    BenchmarkClaim,
    ClaimDelta,
    ClaimVerification,
    PerturbationType,
)

BENCHMARK_PATH = Path("data/benchmark/claims.jsonl")


def build_invariance_baseline(
    claims: list[BenchmarkClaim],
) -> tuple[
    list[BenchmarkClaim],
    dict[str, ClaimVerification],
    dict[str, ClaimDelta | None],
]:
    claims_by_id = {claim.claim_id: claim for claim in claims}

    perturbations = [
        claim for claim in claims if claim.perturbation_type != PerturbationType.NONE
    ]

    verifications: dict[str, ClaimVerification] = {}
    deltas: dict[str, ClaimDelta | None] = {}

    for claim in perturbations:
        if claim.source_claim_id is None:
            raise ValueError(f"Perturbation {claim.claim_id!r} has no source claim.")

        try:
            source_claim = claims_by_id[claim.source_claim_id]
        except KeyError as exc:
            raise ValueError(
                f"Source claim {claim.source_claim_id!r} for "
                f"{claim.claim_id!r} is missing from the benchmark."
            ) from exc

        verifications[claim.claim_id] = ClaimVerification(
            claim_id=claim.claim_id,
            atomic_results=[],
            verdict=source_claim.expected_verdict,
            claim_issues=list(source_claim.expected_claim_issues),
            evidence_issues=list(source_claim.expected_evidence_issues),
            explanation=(
                "Perturbation-invariance baseline: inherited the "
                "source claim's verification state."
            ),
        )

        if source_claim.expected_revised_claim is None:
            deltas[claim.claim_id] = None
        else:
            deltas[claim.claim_id] = ClaimDelta(
                original_claim=claim.text,
                revised_claim=source_claim.expected_revised_claim,
                changes=[],
            )

    return perturbations, verifications, deltas


def format_percentage(value: float) -> str:
    return f"{value:.1%}"


def print_summary(
    *,
    title: str,
    summary: MetricSummary,
) -> None:
    print(title)
    print(f"  Cases:                       {summary.total_cases}")
    print(
        f"  Verdict accuracy:            {format_percentage(summary.verdict_accuracy)}"
    )
    print(
        "  Claim issue exact match:     "
        f"{format_percentage(summary.claim_issue_exact_match)}"
    )
    print(
        "  Evidence issue exact match:  "
        f"{format_percentage(summary.evidence_issue_exact_match)}"
    )
    print(
        "  Correction exact match:      "
        f"{format_percentage(summary.correction_exact_match)}"
    )
    print(
        f"  Full case exact match:       {format_percentage(summary.case_exact_match)}"
    )


def print_metrics(metrics: BenchmarkMetrics) -> None:
    print()
    print("=" * 72)
    print("NUMMARIA VERITAS — ADVERSARIAL PERTURBATION BASELINE")
    print("=" * 72)
    print()
    print(
        "Baseline assumption: each perturbed case receives the same "
        "judgment as its unperturbed source claim."
    )
    print()

    print_summary(
        title="Overall",
        summary=metrics.overall,
    )

    print()
    print("By perturbation type")
    print("-" * 72)

    for perturbation_type, summary in sorted(metrics.by_perturbation_type.items()):
        print_summary(
            title=perturbation_type,
            summary=summary,
        )
        print()

    print("By perturbation target")
    print("-" * 72)

    for perturbation_target, summary in sorted(metrics.by_perturbation_target.items()):
        print_summary(
            title=perturbation_target,
            summary=summary,
        )
        print()

    failures = get_benchmark_failures(metrics)

    print("Failures")
    print("-" * 72)

    if not failures:
        print("None")
        return

    for failure in failures:
        failed_dimensions = ", ".join(failure.failed_dimensions)

        print(f"{failure.claim_id}: {failed_dimensions}")


def main() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    perturbations, verifications, deltas = build_invariance_baseline(claims)

    if not perturbations:
        raise ValueError("The benchmark contains no perturbation cases.")

    metrics = evaluate_benchmark(
        claims=perturbations,
        verifications_by_claim=verifications,
        deltas_by_claim=deltas,
    )

    print_metrics(metrics)


if __name__ == "__main__":
    main()
