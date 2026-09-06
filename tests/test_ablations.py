from datetime import timedelta
from pathlib import Path

from nummaria_veritas.evaluation.ablations import (
    FULL_SYSTEM,
    NO_CAUSAL_CHECK,
    NO_EVIDENCE_INDEPENDENCE,
    NO_NUMERICAL_CONSISTENCY,
    NO_TEMPORAL_VALIDITY,
)
from nummaria_veritas.evaluation.benchmark import load_benchmark
from nummaria_veritas.evaluation.benchmark_runner import (
    resolve_perturbed_evidence_results,
)
from nummaria_veritas.models import (
    AtomicClaim,
    Claim,
    ClaimIssue,
    EvidenceAssessment,
    EvidenceIssue,
    EvidenceResult,
    EvidenceStance,
    PerturbationTarget,
    PerturbationType,
    PropositionType,
    Verdict,
)
from nummaria_veritas.retrieval.corpus import load_chunks
from nummaria_veritas.verification.engine import verify_atomic_claim

BENCHMARK_PATH = Path("data/benchmark/claims.jsonl")
CORPUS_PATH = Path("data/processed/chunks.jsonl")


def test_full_system_detects_redundant_benchmark_evidence() -> None:
    claim, atomic_claim, assessments = _load_redundancy_case()

    result = verify_atomic_claim(
        claim=claim,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=FULL_SYSTEM.config,
    )

    assert result.verdict == Verdict.SUPPORTED_CLAIM
    assert EvidenceIssue.EVIDENCE_REDUNDANCY in result.evidence_issues


def test_evidence_independence_ablation_removes_redundancy_detection() -> None:
    claim, atomic_claim, assessments = _load_redundancy_case()

    result = verify_atomic_claim(
        claim=claim,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=NO_EVIDENCE_INDEPENDENCE.config,
    )

    assert result.verdict == Verdict.SUPPORTED_CLAIM
    assert EvidenceIssue.EVIDENCE_REDUNDANCY not in result.evidence_issues


def test_temporal_ablation_allows_future_support() -> None:
    claim, atomic_claim, evidence = _make_temporal_case()

    assessments = [
        EvidenceAssessment(
            evidence=evidence,
            stance=EvidenceStance.SUPPORTS,
            explanation="The evidence supports the proposition.",
        )
    ]

    full_result = verify_atomic_claim(
        claim=claim,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=FULL_SYSTEM.config,
    )

    ablated_result = verify_atomic_claim(
        claim=claim,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=NO_TEMPORAL_VALIDITY.config,
    )

    assert full_result.verdict == Verdict.INSUFFICIENT_EVIDENCE
    assert ablated_result.verdict == Verdict.SUPPORTED_CLAIM


def test_numerical_ablation_removes_numerical_issue() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    claim = next(
        claim
        for claim in claims
        if claim.perturbation_type == PerturbationType.NUMERICAL
    )

    source_claim = next(
        source for source in claims if source.claim_id == claim.source_claim_id
    )

    evidence = EvidenceResult(
        chunk_id=source_claim.claim_id,
        document_id=source_claim.claim_id,
        company=claim.company,
        document_type="benchmark_source",
        reporting_period=claim.reporting_period or "",
        publication_date=claim.as_of_date,
        page_number=1,
        text=source_claim.text,
        retrieval_score=None,
    )

    atomic_claim = AtomicClaim(
        atomic_claim_id=f"{claim.claim_id}_atomic",
        parent_claim_id=claim.claim_id,
        text=claim.text,
        proposition_type=PropositionType.FACT,
    )

    assessments = [
        EvidenceAssessment(
            evidence=evidence,
            stance=EvidenceStance.SUPPORTS,
            explanation="The evidence supports the underlying proposition.",
        )
    ]

    full_result = verify_atomic_claim(
        claim=claim,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=FULL_SYSTEM.config,
    )

    ablated_result = verify_atomic_claim(
        claim=claim,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=NO_NUMERICAL_CONSISTENCY.config,
    )

    assert ClaimIssue.NUMERICAL_INCONSISTENCY in full_result.claim_issues
    assert ClaimIssue.NUMERICAL_INCONSISTENCY not in ablated_result.claim_issues


def test_causal_ablation_removes_causal_overclaim() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    claim = next(
        claim for claim in claims if claim.perturbation_type == PerturbationType.CAUSAL
    )

    atomic_claim = AtomicClaim(
        atomic_claim_id=f"{claim.claim_id}_atomic",
        parent_claim_id=claim.claim_id,
        text=claim.text,
        proposition_type=PropositionType.RELATION,
        is_causal=True,
    )

    evidence = EvidenceResult(
        chunk_id=claim.claim_id,
        document_id=claim.claim_id,
        company=claim.company,
        document_type="benchmark_source",
        reporting_period=claim.reporting_period or "",
        publication_date=claim.as_of_date,
        page_number=1,
        text=claim.text,
        retrieval_score=None,
    )

    assessments = [
        EvidenceAssessment(
            evidence=evidence,
            stance=EvidenceStance.PARTIALLY_SUPPORTS,
            explanation=(
                "The evidence establishes the underlying facts but does not "
                "establish the asserted causal relationship."
            ),
        )
    ]

    full_result = verify_atomic_claim(
        claim=claim,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=FULL_SYSTEM.config,
    )

    ablated_result = verify_atomic_claim(
        claim=claim,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=NO_CAUSAL_CHECK.config,
    )

    assert full_result.verdict == Verdict.PARTIALLY_SUPPORTED_CLAIM
    assert ClaimIssue.CAUSAL_OVERCLAIM in full_result.claim_issues
    assert full_result.supporting_evidence == [evidence]

    assert ablated_result.verdict == Verdict.PARTIALLY_SUPPORTED_CLAIM
    assert ClaimIssue.CAUSAL_OVERCLAIM not in ablated_result.claim_issues
    assert ablated_result.supporting_evidence == [evidence]


def _load_redundancy_case() -> tuple[
    Claim,
    AtomicClaim,
    list[EvidenceAssessment],
]:
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

    atomic_claim = AtomicClaim(
        atomic_claim_id=f"{claim.claim_id}_atomic",
        parent_claim_id=claim.claim_id,
        text=claim.text,
        proposition_type=PropositionType.FACT,
    )

    assessments = [
        EvidenceAssessment(
            evidence=item,
            stance=EvidenceStance.SUPPORTS,
            explanation="The evidence supports the proposition.",
        )
        for item in evidence
    ]

    return claim, atomic_claim, assessments


def _make_temporal_case() -> tuple[
    Claim,
    AtomicClaim,
    EvidenceResult,
]:
    claims = load_benchmark(BENCHMARK_PATH)

    claim = next(
        claim
        for claim in claims
        if claim.perturbation_type == PerturbationType.TEMPORAL
    )

    source_claim = next(
        source for source in claims if source.claim_id == claim.source_claim_id
    )

    future_publication_date = claim.as_of_date + timedelta(days=1)

    evidence = EvidenceResult(
        chunk_id=source_claim.claim_id,
        document_id=source_claim.claim_id,
        company=claim.company,
        document_type="benchmark_source",
        reporting_period=claim.reporting_period or "",
        publication_date=future_publication_date,
        page_number=1,
        text=source_claim.text,
        retrieval_score=None,
    )

    atomic_claim = AtomicClaim(
        atomic_claim_id=f"{claim.claim_id}_atomic",
        parent_claim_id=claim.claim_id,
        text=claim.text,
        proposition_type=PropositionType.FACT,
    )

    return claim, atomic_claim, evidence
