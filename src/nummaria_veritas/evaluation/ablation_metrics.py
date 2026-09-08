"""Measure targeted capability loss under component ablations."""

from collections.abc import Iterable
from dataclasses import dataclass

from nummaria_veritas.evaluation.ablations import Ablation


@dataclass(frozen=True)
class AblationCaseResult:
    claim_id: str
    perturbation_type: str
    full_system_detected: bool
    ablation_detected: bool


@dataclass(frozen=True)
class AblationResult:
    ablation: Ablation
    cases: tuple[AblationCaseResult, ...]

    @property
    def total_cases(self) -> int:
        return len(self.cases)

    @property
    def full_system_detection_rate(self) -> float:
        return _rate(case.full_system_detected for case in self.cases)

    @property
    def ablation_success_rate(self) -> float:
        return _rate(case.ablation_detected for case in self.cases)


def _rate(values: Iterable[bool]) -> float:
    materialized = tuple(values)

    if not materialized:
        raise ValueError("Cannot calculate an ablation rate without cases.")

    return sum(materialized) / len(materialized)
