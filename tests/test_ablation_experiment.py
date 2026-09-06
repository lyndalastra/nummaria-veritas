from experiments.run_ablations import run_ablation_study
from nummaria_veritas.evaluation.ablations import (
    ABLATIONS,
    FULL_SYSTEM,
)


def test_ablation_study_runs_every_configured_ablation() -> None:
    results = run_ablation_study()

    expected_ablations = {ablation for ablation in ABLATIONS if ablation != FULL_SYSTEM}

    observed_ablations = {result.ablation for result in results}

    assert results
    assert observed_ablations == expected_ablations
    assert len(results) == len(observed_ablations)


def test_full_system_detects_every_targeted_phenomenon() -> None:
    results = run_ablation_study()

    assert results

    for result in results:
        assert result.cases

        assert all(case.full_system_detected for case in result.cases)

        assert result.full_system_detection_rate == 1.0


def test_every_ablation_removes_its_targeted_capability() -> None:
    results = run_ablation_study()

    assert results

    for result in results:
        assert result.cases

        assert all(case.ablation_detected for case in result.cases)

        assert result.ablation_success_rate == 1.0
