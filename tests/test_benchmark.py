import re
from pathlib import Path

from nummaria_veritas.evaluation.benchmark import load_benchmark
from nummaria_veritas.models import (
    PerturbationTarget,
    PerturbationType,
    Verdict,
)
from nummaria_veritas.retrieval.corpus import load_chunks

CORPUS_PATH = Path("data/processed/chunks.jsonl")
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
    PerturbationType.REDUNDANCY: "RED",
}

PERTURBATION_TARGET_CODES = {
    PerturbationTarget.CLAIM: "CLM",
    PerturbationTarget.EVIDENCE: "EVD",
    PerturbationTarget.EVALUATION_CONTEXT: "CTX",
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
        claim for claim in claims if claim.expected_verdict == Verdict.SUPPORTED_CLAIM
    ]

    assert all(claim.expected_revised_claim is None for claim in supported_claims)


def test_supported_claims_do_not_have_claim_issues() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    supported_claims = [
        claim for claim in claims if claim.expected_verdict == Verdict.SUPPORTED_CLAIM
    ]

    assert all(not claim.expected_claim_issues for claim in supported_claims)


def test_original_claims_do_not_have_perturbation_metadata() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    original_claims = [
        claim for claim in claims if claim.perturbation_type == PerturbationType.NONE
    ]

    assert all(
        claim.perturbation_target is None
        and claim.source_claim_id is None
        and not claim.perturbed_evidence
        for claim in original_claims
    )


def test_perturbations_have_targets() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    perturbations = [
        claim for claim in claims if claim.perturbation_type != PerturbationType.NONE
    ]

    assert all(claim.perturbation_target is not None for claim in perturbations)


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
        assert claim.perturbation_target is not None

        perturbation_code = PERTURBATION_CODES[claim.perturbation_type]

        target_code = PERTURBATION_TARGET_CODES[claim.perturbation_target]

        expected_pattern = (
            rf"^{re.escape(claim.source_claim_id)}_"
            rf"{perturbation_code}_"
            rf"{target_code}_"
            rf"\d+$"
        )

        assert re.fullmatch(
            expected_pattern,
            claim.claim_id,
        )


def test_evidence_target_perturbations_identify_perturbed_evidence() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    evidence_perturbations = [
        claim
        for claim in claims
        if claim.perturbation_target == PerturbationTarget.EVIDENCE
    ]

    assert all(claim.perturbed_evidence for claim in evidence_perturbations)


def test_non_evidence_perturbations_do_not_have_perturbed_evidence() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    non_evidence_perturbations = [
        claim
        for claim in claims
        if claim.perturbation_target != PerturbationTarget.EVIDENCE
    ]

    assert all(not claim.perturbed_evidence for claim in non_evidence_perturbations)


def test_perturbed_evidence_has_non_empty_summaries() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    perturbed_evidence = [
        evidence for claim in claims for evidence in claim.perturbed_evidence
    ]

    assert all(evidence.summary.strip() for evidence in perturbed_evidence)


def test_perturbed_evidence_chunk_ids_exist_in_corpus() -> None:
    claims = load_benchmark(BENCHMARK_PATH)
    chunks = load_chunks(CORPUS_PATH)

    corpus_chunk_ids = {chunk.chunk_id for chunk in chunks}

    perturbed_chunk_ids = {
        evidence.chunk_id for claim in claims for evidence in claim.perturbed_evidence
    }

    assert perturbed_chunk_ids <= corpus_chunk_ids


def test_invalid_evidence_cases_have_expected_evidence_issues() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    invalid_evidence_cases = [
        claim for claim in claims if claim.expected_verdict == Verdict.INVALID_EVIDENCE
    ]

    assert all(claim.expected_evidence_issues for claim in invalid_evidence_cases)


def test_redundancy_perturbations_use_multiple_evidence_items() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    redundancy_cases = [
        claim
        for claim in claims
        if claim.perturbation_type == PerturbationType.REDUNDANCY
    ]

    assert redundancy_cases

    assert all(len(claim.perturbed_evidence) > 1 for claim in redundancy_cases)
