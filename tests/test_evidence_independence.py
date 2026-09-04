from pathlib import Path

from nummaria_veritas.evaluation.benchmark import load_benchmark
from nummaria_veritas.evaluation.benchmark_runner import (
    resolve_perturbed_evidence_results,
)
from nummaria_veritas.evidence.independence import (
    assess_evidence_independence,
)
from nummaria_veritas.models import (
    EvidenceIssue,
    PerturbationTarget,
    PerturbationType,
)
from nummaria_veritas.retrieval.corpus import load_chunks

BENCHMARK_PATH = Path("data/benchmark/claims.jsonl")
CORPUS_PATH = Path("data/processed/chunks.jsonl")


def test_redundancy_perturbations_have_fewer_independent_sources_than_evidence_items() -> (
    None
):
    claims = load_benchmark(BENCHMARK_PATH)
    chunks = load_chunks(CORPUS_PATH)

    redundancy_cases = [
        claim
        for claim in claims
        if claim.perturbation_type == PerturbationType.REDUNDANCY
        and claim.perturbation_target == PerturbationTarget.EVIDENCE
    ]

    assert redundancy_cases

    for claim in redundancy_cases:
        evidence = resolve_perturbed_evidence_results(
            claim=claim,
            chunks=chunks,
        )

        assert evidence is not None

        result = assess_evidence_independence(evidence)

        assert result.raw_evidence_count == len(evidence)

        assert result.independent_evidence_count < result.raw_evidence_count

        assert result.redundant_evidence_count > 0

        assert EvidenceIssue.EVIDENCE_REDUNDANCY in result.evidence_issues


def test_redundancy_clusters_preserve_all_declared_evidence() -> None:
    claims = load_benchmark(BENCHMARK_PATH)
    chunks = load_chunks(CORPUS_PATH)

    redundancy_cases = [
        claim
        for claim in claims
        if claim.perturbation_type == PerturbationType.REDUNDANCY
        and claim.perturbation_target == PerturbationTarget.EVIDENCE
    ]

    assert redundancy_cases

    for claim in redundancy_cases:
        evidence = resolve_perturbed_evidence_results(
            claim=claim,
            chunks=chunks,
        )

        assert evidence is not None

        result = assess_evidence_independence(evidence)

        clustered_chunk_ids = {
            item.chunk_id for cluster in result.clusters for item in cluster.evidence
        }

        declared_chunk_ids = {item.chunk_id for item in evidence}

        assert clustered_chunk_ids == declared_chunk_ids


def test_single_evidence_item_is_not_redundant() -> None:
    claims = load_benchmark(BENCHMARK_PATH)
    chunks = load_chunks(CORPUS_PATH)

    single_evidence_cases = [
        claim
        for claim in claims
        if claim.perturbation_target == PerturbationTarget.EVIDENCE
        and len(claim.perturbed_evidence) == 1
    ]

    assert single_evidence_cases

    for claim in single_evidence_cases:
        evidence = resolve_perturbed_evidence_results(
            claim=claim,
            chunks=chunks,
        )

        assert evidence is not None

        result = assess_evidence_independence(evidence)

        assert result.raw_evidence_count == len(evidence)
        assert result.independent_evidence_count == len(evidence)
        assert result.redundant_evidence_count == 0

        assert EvidenceIssue.EVIDENCE_REDUNDANCY not in result.evidence_issues


def test_empty_evidence_has_no_redundancy() -> None:
    result = assess_evidence_independence([])

    assert result.clusters == ()
    assert result.raw_evidence_count == 0
    assert result.independent_evidence_count == 0
    assert result.redundant_evidence_count == 0
    assert result.evidence_issues == ()
