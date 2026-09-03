import re
from pathlib import Path

from nummaria_veritas.evaluation.benchmark import load_benchmark
from nummaria_veritas.models import PerturbationType, Verdict

BENCHMARK_PATH = Path("data/benchmark/claims.jsonl")

PERTURBATION_CODES = {
    PerturbationType.NUMERICAL: "NUM",
    PerturbationType.METRIC: "MET",
    PerturbationType.PERIOD: "PER",
    PerturbationType.SCOPE: "SCP",
    PerturbationType.TEMPORAL: "TMP",
    PerturbationType.REPRESENTATION: "REP",
    PerturbationType.FORECAST_AS_FACT: "FCT",
    PerturbationType.CAUSAL: "CAU",
    PerturbationType.COMPOSITIONAL: "CMP",
    PerturbationType.ENTITY: "ENT",
}


def test_benchmark_is_not_empty() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    assert claims


def test_claim_ids_are_unique() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    claim_ids = [claim.claim_id for claim in claims]

    assert len(claim_ids) == len(set(claim_ids))


def test_all_claims_have_company_names() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    assert all(claim.company.strip() for claim in claims)


def test_supported_claims_do_not_have_revisions() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    supported_claims = [
        claim for claim in claims if claim.expected_verdict == Verdict.SUPPORTED
    ]

    assert all(claim.expected_revised_claim is None for claim in supported_claims)


def test_supported_claims_do_not_have_expected_issues() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    supported_claims = [
        claim
        for claim in claims
        if claim.expected_verdict
        == Verdict.SUPPORTED
    ]

    assert all(
        not claim.expected_claim_issues
        and not claim.expected_evidence_issues
        for claim in supported_claims
    )


def test_original_claims_do_not_reference_source_claims() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    original_claims = [
        claim for claim in claims if claim.perturbation_type == PerturbationType.NONE
    ]

    assert all(claim.source_claim_id is None for claim in original_claims)


def test_perturbations_reference_existing_source_claims() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    claim_ids = {claim.claim_id for claim in claims}

    perturbations = [
        claim for claim in claims if claim.perturbation_type != PerturbationType.NONE
    ]

    assert all(
        claim.source_claim_id is not None
        and claim.source_claim_id in claim_ids
        and claim.source_claim_id != claim.claim_id
        for claim in perturbations
    )


def test_perturbation_ids_follow_family_naming_convention() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    perturbations = [
        claim for claim in claims if claim.perturbation_type != PerturbationType.NONE
    ]

    for claim in perturbations:
        assert claim.source_claim_id is not None

        perturbation_code = PERTURBATION_CODES[claim.perturbation_type]

        expected_pattern = (
            rf"^{re.escape(claim.source_claim_id)}_"
            rf"{perturbation_code}_"
            rf"\d+$"
        )

        assert re.fullmatch(
            expected_pattern,
            claim.claim_id,
        )
