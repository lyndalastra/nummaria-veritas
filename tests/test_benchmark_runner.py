import re
from pathlib import Path

import pytest

from nummaria_veritas.evaluation.benchmark import load_benchmark
from nummaria_veritas.evaluation.benchmark_runner import (
    resolve_perturbed_evidence,
    resolve_perturbed_evidence_results,
)
from nummaria_veritas.models import PerturbationTarget
from nummaria_veritas.retrieval.corpus import load_chunks

BENCHMARK_PATH = Path("data/benchmark/claims.jsonl")
CORPUS_PATH = Path("data/processed/chunks.jsonl")


def test_evidence_perturbations_resolve_all_declared_chunks() -> None:
    claims = load_benchmark(BENCHMARK_PATH)
    chunks = load_chunks(CORPUS_PATH)

    evidence_perturbations = [
        claim
        for claim in claims
        if claim.perturbation_target == PerturbationTarget.EVIDENCE
    ]

    assert evidence_perturbations

    for claim in evidence_perturbations:
        resolved = resolve_perturbed_evidence(
            claim=claim,
            chunks=chunks,
        )

        assert resolved is not None

        declared_chunk_ids = [
            evidence.chunk_id for evidence in claim.perturbed_evidence
        ]

        resolved_chunk_ids = [chunk.chunk_id for chunk in resolved]

        assert resolved_chunk_ids == declared_chunk_ids


def test_non_evidence_perturbations_do_not_inject_evidence() -> None:
    claims = load_benchmark(BENCHMARK_PATH)
    chunks = load_chunks(CORPUS_PATH)

    non_evidence_cases = [
        claim
        for claim in claims
        if claim.perturbation_target != PerturbationTarget.EVIDENCE
    ]

    assert non_evidence_cases

    for claim in non_evidence_cases:
        resolved = resolve_perturbed_evidence(
            claim=claim,
            chunks=chunks,
        )

        assert resolved is None


def test_missing_perturbed_evidence_chunks_are_rejected() -> None:
    claims = load_benchmark(BENCHMARK_PATH)
    chunks = load_chunks(CORPUS_PATH)

    evidence_perturbations = [
        claim
        for claim in claims
        if claim.perturbation_target == PerturbationTarget.EVIDENCE
    ]

    assert evidence_perturbations

    for claim in evidence_perturbations:
        declared_chunk_ids = {
            evidence.chunk_id for evidence in claim.perturbed_evidence
        }

        chunks_without_declared_evidence = [
            chunk for chunk in chunks if chunk.chunk_id not in declared_chunk_ids
        ]

        with pytest.raises(ValueError) as exc_info:
            resolve_perturbed_evidence(
                claim=claim,
                chunks=chunks_without_declared_evidence,
            )

        error_message = str(exc_info.value)

        assert all(
            re.search(re.escape(chunk_id), error_message)
            for chunk_id in declared_chunk_ids
        )


def test_evidence_perturbations_become_verification_ready_results() -> None:
    claims = load_benchmark(BENCHMARK_PATH)
    chunks = load_chunks(CORPUS_PATH)

    chunks_by_id = {chunk.chunk_id: chunk for chunk in chunks}

    evidence_perturbations = [
        claim
        for claim in claims
        if claim.perturbation_target == PerturbationTarget.EVIDENCE
    ]

    assert evidence_perturbations

    for claim in evidence_perturbations:
        results = resolve_perturbed_evidence_results(
            claim=claim,
            chunks=chunks,
        )

        assert results is not None

        assert [result.chunk_id for result in results] == [
            evidence.chunk_id for evidence in claim.perturbed_evidence
        ]

        for result in results:
            source_chunk = chunks_by_id[result.chunk_id]

            assert result.document_id == source_chunk.document_id
            assert result.company == source_chunk.company
            assert result.document_type == source_chunk.document_type
            assert result.reporting_period == source_chunk.reporting_period
            assert result.publication_date == source_chunk.publication_date
            assert result.page_number == source_chunk.page_number
            assert result.text == source_chunk.text

            assert result.retrieval_score is None
