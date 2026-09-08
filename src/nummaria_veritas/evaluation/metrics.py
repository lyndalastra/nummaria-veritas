from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from nummaria_veritas.models import (
    BenchmarkClaim,
    ClaimDelta,
    ClaimVerification,
)


@dataclass(frozen=True)
class BenchmarkCaseEvaluation:
    claim_id: str
    perturbation_type: str
    perturbation_target: str | None
    verdict_match: bool
    claim_issues_match: bool
    evidence_issues_match: bool
    correction_match: bool

    @property
    def exact_match(self) -> bool:
        return (
            self.verdict_match
            and self.claim_issues_match
            and self.evidence_issues_match
            and self.correction_match
        )

    @property
    def failed_dimensions(self) -> tuple[str, ...]:
        failures: list[str] = []

        if not self.verdict_match:
            failures.append("verdict")

        if not self.claim_issues_match:
            failures.append("claim_issues")

        if not self.evidence_issues_match:
            failures.append("evidence_issues")

        if not self.correction_match:
            failures.append("correction")

        return tuple(failures)


@dataclass(frozen=True)
class MetricSummary:
    total_cases: int
    verdict_accuracy: float
    claim_issue_exact_match: float
    evidence_issue_exact_match: float
    correction_exact_match: float
    case_exact_match: float


@dataclass(frozen=True)
class BenchmarkMetrics:
    overall: MetricSummary
    by_perturbation_type: dict[str, MetricSummary]
    by_perturbation_target: dict[str, MetricSummary]
    cases: tuple[BenchmarkCaseEvaluation, ...]


def evaluate_benchmark(
    *,
    claims: Sequence[BenchmarkClaim],
    verifications_by_claim: Mapping[str, ClaimVerification],
    deltas_by_claim: Mapping[str, ClaimDelta | None] | None = None,
) -> BenchmarkMetrics:
    """Compare predicted benchmark outputs with their gold verification state."""

    if not claims:
        raise ValueError("Cannot evaluate an empty benchmark.")

    missing_claim_ids = [
        claim.claim_id
        for claim in claims
        if claim.claim_id not in verifications_by_claim
    ]

    if missing_claim_ids:
        missing_ids = ", ".join(missing_claim_ids)

        raise ValueError(
            f"Missing verification results for benchmark claims: {missing_ids}"
        )

    delta_lookup = deltas_by_claim or {}

    case_results = tuple(
        _evaluate_case(
            claim=claim,
            verification=verifications_by_claim[claim.claim_id],
            delta=delta_lookup.get(claim.claim_id),
        )
        for claim in claims
    )

    return BenchmarkMetrics(
        overall=_summarize(case_results),
        by_perturbation_type=_summarize_by_perturbation_type(
            claims=claims,
            case_results=case_results,
        ),
        by_perturbation_target=_summarize_by_perturbation_target(
            claims=claims,
            case_results=case_results,
        ),
        cases=case_results,
    )


def get_benchmark_failures(
    metrics: BenchmarkMetrics,
) -> tuple[BenchmarkCaseEvaluation, ...]:
    return tuple(case for case in metrics.cases if not case.exact_match)


def _evaluate_case(
    *,
    claim: BenchmarkClaim,
    verification: ClaimVerification,
    delta: ClaimDelta | None,
) -> BenchmarkCaseEvaluation:
    if verification.claim_id != claim.claim_id:
        raise ValueError(
            f"Verification result {verification.claim_id!r} does not "
            f"match benchmark claim {claim.claim_id!r}."
        )

    actual_revised_claim = delta.revised_claim if delta is not None else None

    return BenchmarkCaseEvaluation(
        claim_id=claim.claim_id,
        perturbation_type=claim.perturbation_type.value,
        perturbation_target=(
            claim.perturbation_target.value
            if claim.perturbation_target is not None
            else None
        ),
        verdict_match=(verification.verdict == claim.expected_verdict),
        claim_issues_match=(
            set(verification.claim_issues) == set(claim.expected_claim_issues)
        ),
        evidence_issues_match=(
            set(verification.evidence_issues) == set(claim.expected_evidence_issues)
        ),
        correction_match=(actual_revised_claim == claim.expected_revised_claim),
    )


def _summarize(
    cases: Sequence[BenchmarkCaseEvaluation],
) -> MetricSummary:
    if not cases:
        raise ValueError("Cannot summarize an empty set of benchmark cases.")

    total = len(cases)

    return MetricSummary(
        total_cases=total,
        verdict_accuracy=sum(case.verdict_match for case in cases) / total,
        claim_issue_exact_match=sum(case.claim_issues_match for case in cases) / total,
        evidence_issue_exact_match=sum(case.evidence_issues_match for case in cases)
        / total,
        correction_exact_match=sum(case.correction_match for case in cases) / total,
        case_exact_match=sum(case.exact_match for case in cases) / total,
    )


def _summarize_by_perturbation_type(
    *,
    claims: Sequence[BenchmarkClaim],
    case_results: Sequence[BenchmarkCaseEvaluation],
) -> dict[str, MetricSummary]:
    grouped: dict[str, list[BenchmarkCaseEvaluation]] = defaultdict(list)

    for claim, case_result in zip(
        claims,
        case_results,
        strict=True,
    ):
        grouped[claim.perturbation_type.value].append(case_result)

    return {
        perturbation_type: _summarize(group)
        for perturbation_type, group in grouped.items()
    }


def _summarize_by_perturbation_target(
    *,
    claims: Sequence[BenchmarkClaim],
    case_results: Sequence[BenchmarkCaseEvaluation],
) -> dict[str, MetricSummary]:
    grouped: dict[str, list[BenchmarkCaseEvaluation]] = defaultdict(list)

    for claim, case_result in zip(
        claims,
        case_results,
        strict=True,
    ):
        target = (
            claim.perturbation_target.value
            if claim.perturbation_target is not None
            else "none"
        )

        grouped[target].append(case_result)

    return {
        perturbation_target: _summarize(group)
        for perturbation_target, group in grouped.items()
    }
