from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from nummaria_veritas.evaluation.ablation_metrics import (
    AblationCaseResult,
    AblationResult,
)
from nummaria_veritas.evaluation.ablations import ABLATIONS, Ablation
from nummaria_veritas.evaluation.benchmark import load_benchmark
from nummaria_veritas.models import PerturbationType

BENCHMARK_PATH = Path("data/benchmark/claims.jsonl")

PERTURBATIONS = tuple(
    claim
    for claim in load_benchmark(BENCHMARK_PATH)
    if claim.perturbation_type != PerturbationType.NONE
)


@given(
    ablation=st.sampled_from(ABLATIONS),
    full_system_outcomes=st.lists(
        st.booleans(),
        min_size=len(PERTURBATIONS),
        max_size=len(PERTURBATIONS),
    ),
    ablation_outcomes=st.lists(
        st.booleans(),
        min_size=len(PERTURBATIONS),
        max_size=len(PERTURBATIONS),
    ),
)
def test_ablation_result_derives_rates_from_case_outcomes(
    ablation: Ablation,
    full_system_outcomes: list[bool],
    ablation_outcomes: list[bool],
) -> None:
    assert PERTURBATIONS

    cases = tuple(
        AblationCaseResult(
            claim_id=claim.claim_id,
            perturbation_type=claim.perturbation_type.value,
            full_system_detected=full_system_detected,
            ablation_detected=ablation_detected,
        )
        for claim, full_system_detected, ablation_detected in zip(
            PERTURBATIONS,
            full_system_outcomes,
            ablation_outcomes,
            strict=True,
        )
    )

    result = AblationResult(
        ablation=ablation,
        cases=cases,
    )

    assert result.total_cases == len(PERTURBATIONS)

    assert result.full_system_detection_rate == (
        sum(full_system_outcomes) / len(full_system_outcomes)
    )

    assert result.ablation_success_rate == (
        sum(ablation_outcomes) / len(ablation_outcomes)
    )
