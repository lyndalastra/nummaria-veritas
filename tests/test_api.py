import logging
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from nummaria_veritas.api.app import app
from nummaria_veritas.evaluation.benchmark import load_benchmark
from nummaria_veritas.evaluation.benchmark_runner import (
    resolve_perturbed_evidence_results,
)
from nummaria_veritas.models import (
    EvidenceIssue,
    EvidenceStance,
    PerturbationTarget,
    PerturbationType,
    PropositionType,
    Verdict,
)
from nummaria_veritas.retrieval.corpus import load_chunks

BENCHMARK_PATH = Path("data/benchmark/claims.jsonl")
CORPUS_PATH = Path("data/processed/chunks.jsonl")

client = TestClient(app)


def test_health_endpoint_reports_service_is_available() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }


def test_verify_endpoint_returns_structured_verification() -> None:
    claims = load_benchmark(BENCHMARK_PATH)
    chunks = load_chunks(CORPUS_PATH)

    claim = next(
        claim
        for claim in claims
        if claim.perturbation_type == PerturbationType.REDUNDANCY
        and claim.perturbation_target == PerturbationTarget.EVIDENCE
    )

    evidence = resolve_perturbed_evidence_results(
        claim=claim,
        chunks=chunks,
    )

    assert evidence is not None

    response = client.post(
        "/verify",
        json={
            "claim_id": claim.claim_id,
            "company": claim.company,
            "text": claim.text,
            "as_of_date": claim.as_of_date.isoformat(),
            "reporting_period": claim.reporting_period,
            "atomic_claims": [
                {
                    "atomic_claim_id": f"{claim.claim_id}_atomic",
                    "text": claim.text,
                    "proposition_type": PropositionType.FACT.value,
                    "evidence": [
                        {
                            "chunk_id": item.chunk_id,
                            "document_id": item.document_id,
                            "company": item.company,
                            "document_type": item.document_type,
                            "reporting_period": item.reporting_period,
                            "publication_date": (item.publication_date.isoformat()),
                            "page_number": item.page_number,
                            "text": item.text,
                            "retrieval_score": item.retrieval_score,
                            "stance": EvidenceStance.SUPPORTS.value,
                            "assessment_explanation": (
                                "The evidence supports the proposition."
                            ),
                        }
                        for item in evidence
                    ],
                }
            ],
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["claim_id"] == claim.claim_id
    assert payload["verdict"] == Verdict.SUPPORTED_CLAIM.value

    assert EvidenceIssue.EVIDENCE_REDUNDANCY.value in payload["evidence_issues"]

    assert len(payload["atomic_results"]) == 1

    atomic_result = payload["atomic_results"][0]

    assert atomic_result["verdict"] == Verdict.SUPPORTED_CLAIM.value

    assert EvidenceIssue.EVIDENCE_REDUNDANCY.value in atomic_result["evidence_issues"]

    assert {item["chunk_id"] for item in atomic_result["supporting_evidence"]} == {
        item.chunk_id for item in evidence
    }


def test_verify_endpoint_logs_completion(
    caplog: pytest.LogCaptureFixture,
) -> None:
    claims = load_benchmark(BENCHMARK_PATH)
    chunks = load_chunks(CORPUS_PATH)

    claim = next(
        claim
        for claim in claims
        if claim.perturbation_type == PerturbationType.REDUNDANCY
        and claim.perturbation_target == PerturbationTarget.EVIDENCE
    )

    evidence = resolve_perturbed_evidence_results(
        claim=claim,
        chunks=chunks,
    )

    assert evidence is not None

    caplog.set_level(
        logging.INFO,
        logger="nummaria_veritas.api.app",
    )

    response = client.post(
        "/verify",
        json={
            "claim_id": claim.claim_id,
            "company": claim.company,
            "text": claim.text,
            "as_of_date": claim.as_of_date.isoformat(),
            "reporting_period": claim.reporting_period,
            "atomic_claims": [
                {
                    "atomic_claim_id": f"{claim.claim_id}_atomic",
                    "text": claim.text,
                    "proposition_type": PropositionType.FACT.value,
                    "evidence": [
                        {
                            "chunk_id": item.chunk_id,
                            "document_id": item.document_id,
                            "company": item.company,
                            "document_type": item.document_type,
                            "reporting_period": item.reporting_period,
                            "publication_date": (item.publication_date.isoformat()),
                            "page_number": item.page_number,
                            "text": item.text,
                            "retrieval_score": item.retrieval_score,
                            "stance": EvidenceStance.SUPPORTS.value,
                            "assessment_explanation": (
                                "The evidence supports the proposition."
                            ),
                        }
                        for item in evidence
                    ],
                }
            ],
        },
    )

    assert response.status_code == 200

    assert any(
        record.getMessage().startswith(
            f"Verification completed claim_id={claim.claim_id}"
        )
        for record in caplog.records
    )


def test_verify_endpoint_rejects_invalid_request_structure() -> None:
    response = client.post(
        "/verify",
        json={},
    )

    assert response.status_code == 422
