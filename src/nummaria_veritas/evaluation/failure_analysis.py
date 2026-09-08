"""Analyse benchmark failures across verification output dimensions."""

from collections import Counter
from dataclasses import dataclass
from enum import Enum

from nummaria_veritas.evaluation.metrics import BenchmarkCaseEvaluation


class FailureDimension(str, Enum):
    VERDICT = "verdict"
    CLAIM_ISSUES = "claim_issues"
    EVIDENCE_ISSUES = "evidence_issues"
    CORRECTION = "correction"


@dataclass(frozen=True)
class FailureRecord:
    claim_id: str
    perturbation_type: str
    perturbation_target: str | None
    failed_dimensions: tuple[FailureDimension, ...]

    @property
    def is_failure(self) -> bool:
        return bool(self.failed_dimensions)

    @property
    def is_full_match(self) -> bool:
        return not self.failed_dimensions


@dataclass(frozen=True)
class FailureSummary:
    records: tuple[FailureRecord, ...]

    @property
    def total_cases(self) -> int:
        return len(self.records)

    @property
    def failed_cases(self) -> int:
        return sum(record.is_failure for record in self.records)

    @property
    def full_match_cases(self) -> int:
        return sum(record.is_full_match for record in self.records)

    @property
    def failure_rate(self) -> float:
        return _rate(self.failed_cases, self.total_cases)

    @property
    def full_match_rate(self) -> float:
        return _rate(self.full_match_cases, self.total_cases)


def analyse_failures(
    evaluations: tuple[BenchmarkCaseEvaluation, ...],
) -> FailureSummary:
    return FailureSummary(
        records=tuple(_build_failure_record(evaluation) for evaluation in evaluations)
    )


def failure_counts_by_dimension(
    summary: FailureSummary,
) -> Counter[FailureDimension]:
    return Counter(
        dimension
        for record in summary.records
        for dimension in record.failed_dimensions
    )


def failure_counts_by_perturbation_type(
    summary: FailureSummary,
) -> Counter[str]:
    return Counter(
        record.perturbation_type for record in summary.records if record.is_failure
    )


def case_counts_by_perturbation_type(
    summary: FailureSummary,
) -> Counter[str]:
    return Counter(record.perturbation_type for record in summary.records)


def failure_counts_by_perturbation_target(
    summary: FailureSummary,
) -> Counter[str | None]:
    return Counter(
        record.perturbation_target for record in summary.records if record.is_failure
    )


def case_counts_by_perturbation_target(
    summary: FailureSummary,
) -> Counter[str | None]:
    return Counter(record.perturbation_target for record in summary.records)


def failure_signature_counts(
    summary: FailureSummary,
) -> Counter[tuple[FailureDimension, ...]]:
    return Counter(record.failed_dimensions for record in summary.records)


def _build_failure_record(
    evaluation: BenchmarkCaseEvaluation,
) -> FailureRecord:
    failed_dimensions: list[FailureDimension] = []

    if not evaluation.verdict_match:
        failed_dimensions.append(FailureDimension.VERDICT)

    if not evaluation.claim_issues_match:
        failed_dimensions.append(FailureDimension.CLAIM_ISSUES)

    if not evaluation.evidence_issues_match:
        failed_dimensions.append(FailureDimension.EVIDENCE_ISSUES)

    if not evaluation.correction_match:
        failed_dimensions.append(FailureDimension.CORRECTION)

    return FailureRecord(
        claim_id=evaluation.claim_id,
        perturbation_type=evaluation.perturbation_type,
        perturbation_target=evaluation.perturbation_target,
        failed_dimensions=tuple(failed_dimensions),
    )


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        raise ValueError("Cannot calculate a failure-analysis rate without cases.")

    return numerator / denominator
