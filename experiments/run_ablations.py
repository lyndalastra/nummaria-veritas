"""Run targeted component ablation experiments."""

from pathlib import Path

from nummaria_veritas.evaluation.ablation_metrics import (
    AblationCaseResult,
    AblationResult,
)
from nummaria_veritas.evaluation.ablations import (
    FULL_SYSTEM,
    NO_CAUSAL_CHECK,
    NO_EVIDENCE_INDEPENDENCE,
    NO_NUMERICAL_CONSISTENCY,
    NO_TEMPORAL_VALIDITY,
    Ablation,
)
from nummaria_veritas.evaluation.benchmark import load_benchmark
from nummaria_veritas.evaluation.benchmark_runner import (
    resolve_perturbed_evidence_results,
)
from nummaria_veritas.models import (
    AtomicClaim,
    BenchmarkClaim,
    ClaimIssue,
    EvidenceAssessment,
    EvidenceIssue,
    EvidenceResult,
    EvidenceStance,
    IngestedChunk,
    PerturbationTarget,
    PerturbationType,
    PropositionType,
    Verdict,
)
from nummaria_veritas.retrieval.corpus import load_chunks
from nummaria_veritas.verification.engine import verify_atomic_claim

BENCHMARK_PATH = Path("data/benchmark/claims.jsonl")
CORPUS_PATH = Path("data/processed/chunks.jsonl")


def run_ablation_study() -> tuple[AblationResult, ...]:
    claims = load_benchmark(BENCHMARK_PATH)
    chunks = load_chunks(CORPUS_PATH)

    return (
        _run_temporal_ablation(
            claims=claims,
            chunks=chunks,
        ),
        _run_numerical_ablation(
            claims=claims,
            chunks=chunks,
        ),
        _run_causal_ablation(
            claims=claims,
            chunks=chunks,
        ),
        _run_independence_ablation(
            claims=claims,
            chunks=chunks,
        ),
    )


def _run_temporal_ablation(
    *,
    claims: list[BenchmarkClaim],
    chunks: list[IngestedChunk],
) -> AblationResult:
    case = _get_perturbation_case(
        claims=claims,
        perturbation_type=PerturbationType.TEMPORAL,
    )

    source = _get_source_claim(
        case=case,
        claims=claims,
    )

    evidence = _resolve_source_evidence(
        source_claim=source,
        chunks=chunks,
    )

    atomic_claim = _make_atomic_claim(
        claim=case,
        proposition_type=PropositionType.FACT,
    )

    assessments = [
        EvidenceAssessment(
            evidence=evidence,
            stance=EvidenceStance.SUPPORTS,
            explanation=(
                "The evidence establishes the proposition but is not "
                "available by the perturbed evaluation date."
            ),
        )
    ]

    full_result = verify_atomic_claim(
        claim=case,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=FULL_SYSTEM.config,
    )

    ablated_result = verify_atomic_claim(
        claim=case,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=NO_TEMPORAL_VALIDITY.config,
    )

    full_system_detected = full_result.verdict == Verdict.INSUFFICIENT_EVIDENCE

    ablation_detected = (
        full_system_detected and ablated_result.verdict != Verdict.INSUFFICIENT_EVIDENCE
    )

    return _single_case_result(
        ablation=NO_TEMPORAL_VALIDITY,
        claim=case,
        full_system_detected=full_system_detected,
        ablation_detected=ablation_detected,
    )


def _run_numerical_ablation(
    *,
    claims: list[BenchmarkClaim],
    chunks: list[IngestedChunk],
) -> AblationResult:
    case = _get_perturbation_case(
        claims=claims,
        perturbation_type=PerturbationType.NUMERICAL,
    )

    source = _get_source_claim(
        case=case,
        claims=claims,
    )

    evidence = _resolve_source_evidence(
        source_claim=source,
        chunks=chunks,
    )

    atomic_claim = _make_atomic_claim(
        claim=case,
        proposition_type=PropositionType.FACT,
    )

    assessments = [
        EvidenceAssessment(
            evidence=evidence,
            stance=EvidenceStance.CONTRADICTS,
            explanation=(
                "The evidence establishes a numerical value "
                "incompatible with the perturbed claim."
            ),
        )
    ]

    full_result = verify_atomic_claim(
        claim=case,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=FULL_SYSTEM.config,
    )

    ablated_result = verify_atomic_claim(
        claim=case,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=NO_NUMERICAL_CONSISTENCY.config,
    )

    full_system_detected = (
        ClaimIssue.NUMERICAL_INCONSISTENCY in full_result.claim_issues
    )

    ablation_detected = (
        full_system_detected
        and ClaimIssue.NUMERICAL_INCONSISTENCY not in ablated_result.claim_issues
    )

    return _single_case_result(
        ablation=NO_NUMERICAL_CONSISTENCY,
        claim=case,
        full_system_detected=full_system_detected,
        ablation_detected=ablation_detected,
    )


def _run_causal_ablation(
    *,
    claims: list[BenchmarkClaim],
    chunks: list[IngestedChunk],
) -> AblationResult:
    case = _get_perturbation_case(
        claims=claims,
        perturbation_type=PerturbationType.CAUSAL,
    )

    source = _get_source_claim(
        case=case,
        claims=claims,
    )

    evidence = _resolve_source_evidence(
        source_claim=source,
        chunks=chunks,
    )

    atomic_claim = _make_atomic_claim(
        claim=case,
        proposition_type=PropositionType.RELATION,
        is_causal=True,
    )

    assessments = [
        EvidenceAssessment(
            evidence=evidence,
            stance=EvidenceStance.PARTIALLY_SUPPORTS,
            explanation=(
                "The evidence establishes the underlying financial facts "
                "but does not establish the asserted causal relationship."
            ),
        )
    ]

    full_result = verify_atomic_claim(
        claim=case,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=FULL_SYSTEM.config,
    )

    ablated_result = verify_atomic_claim(
        claim=case,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=NO_CAUSAL_CHECK.config,
    )

    full_system_detected = ClaimIssue.CAUSAL_OVERCLAIM in full_result.claim_issues

    ablation_detected = (
        full_system_detected
        and ClaimIssue.CAUSAL_OVERCLAIM not in ablated_result.claim_issues
    )

    return _single_case_result(
        ablation=NO_CAUSAL_CHECK,
        claim=case,
        full_system_detected=full_system_detected,
        ablation_detected=ablation_detected,
    )


def _run_independence_ablation(
    *,
    claims: list[BenchmarkClaim],
    chunks: list[IngestedChunk],
) -> AblationResult:
    case = next(
        claim
        for claim in claims
        if claim.perturbation_type == PerturbationType.REDUNDANCY
        and claim.perturbation_target == PerturbationTarget.EVIDENCE
    )

    evidence = resolve_perturbed_evidence_results(
        claim=case,
        chunks=chunks,
    )

    if evidence is None:
        raise ValueError(
            f"Redundancy case {case.claim_id!r} has no perturbed evidence."
        )

    atomic_claim = _make_atomic_claim(
        claim=case,
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

    full_result = verify_atomic_claim(
        claim=case,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=FULL_SYSTEM.config,
    )

    ablated_result = verify_atomic_claim(
        claim=case,
        atomic_claim=atomic_claim,
        assessments=assessments,
        config=NO_EVIDENCE_INDEPENDENCE.config,
    )

    full_system_detected = (
        EvidenceIssue.EVIDENCE_REDUNDANCY in full_result.evidence_issues
    )

    ablation_detected = (
        full_system_detected
        and EvidenceIssue.EVIDENCE_REDUNDANCY not in ablated_result.evidence_issues
    )

    return _single_case_result(
        ablation=NO_EVIDENCE_INDEPENDENCE,
        claim=case,
        full_system_detected=full_system_detected,
        ablation_detected=ablation_detected,
    )


def _resolve_source_evidence(
    *,
    source_claim: BenchmarkClaim,
    chunks: list[IngestedChunk],
) -> EvidenceResult:
    candidates = [
        chunk
        for chunk in chunks
        if chunk.company == source_claim.company
        and chunk.reporting_period == source_claim.reporting_period
        and chunk.publication_date <= source_claim.as_of_date
    ]

    if not candidates:
        raise ValueError(
            f"No admissible corpus evidence found for "
            f"source claim {source_claim.claim_id!r}."
        )

    source_terms = _normalised_terms(source_claim.text)

    best_chunk = max(
        candidates,
        key=lambda chunk: len(source_terms.intersection(_normalised_terms(chunk.text))),
    )

    if not source_terms.intersection(_normalised_terms(best_chunk.text)):
        raise ValueError(
            f"No relevant corpus evidence found for "
            f"source claim {source_claim.claim_id!r}."
        )

    return EvidenceResult(
        chunk_id=best_chunk.chunk_id,
        document_id=best_chunk.document_id,
        company=best_chunk.company,
        document_type=best_chunk.document_type,
        reporting_period=best_chunk.reporting_period,
        publication_date=best_chunk.publication_date,
        page_number=best_chunk.page_number,
        text=best_chunk.text,
        retrieval_score=None,
    )


def _normalised_terms(text: str) -> set[str]:
    return {
        token.strip(".,:;!?()[]{}'\"").casefold()
        for token in text.split()
        if token.strip(".,:;!?()[]{}'\"")
    }


def _get_perturbation_case(
    *,
    claims: list[BenchmarkClaim],
    perturbation_type: PerturbationType,
) -> BenchmarkClaim:
    matches = [
        claim for claim in claims if claim.perturbation_type == perturbation_type
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one {perturbation_type.value!r} "
            f"perturbation, found {len(matches)}."
        )

    return matches[0]


def _get_source_claim(
    *,
    case: BenchmarkClaim,
    claims: list[BenchmarkClaim],
) -> BenchmarkClaim:
    if case.source_claim_id is None:
        raise ValueError(f"Perturbation {case.claim_id!r} has no source claim.")

    matches = [claim for claim in claims if claim.claim_id == case.source_claim_id]

    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one source claim "
            f"{case.source_claim_id!r}, found {len(matches)}."
        )

    return matches[0]


def _make_atomic_claim(
    *,
    claim: BenchmarkClaim,
    proposition_type: PropositionType,
    is_causal: bool = False,
) -> AtomicClaim:
    return AtomicClaim(
        atomic_claim_id=f"{claim.claim_id}_atomic",
        parent_claim_id=claim.claim_id,
        text=claim.text,
        proposition_type=proposition_type,
        is_causal=is_causal,
    )


def _single_case_result(
    *,
    ablation: Ablation,
    claim: BenchmarkClaim,
    full_system_detected: bool,
    ablation_detected: bool,
) -> AblationResult:
    return AblationResult(
        ablation=ablation,
        cases=(
            AblationCaseResult(
                claim_id=claim.claim_id,
                perturbation_type=claim.perturbation_type.value,
                full_system_detected=full_system_detected,
                ablation_detected=ablation_detected,
            ),
        ),
    )


def _format_percentage(value: float) -> str:
    return f"{value:.1%}"


def print_results(
    results: tuple[AblationResult, ...],
) -> None:
    print()
    print("=" * 80)
    print("NUMMARIA VERITAS — COMPONENT ABLATION STUDY")
    print("=" * 80)
    print()

    print(f"{'Configuration':<38}{'Full detection':>18}{'Ablation success':>20}")
    print("-" * 76)

    for result in results:
        print(
            f"{result.ablation.name:<38}"
            f"{_format_percentage(result.full_system_detection_rate):>18}"
            f"{_format_percentage(result.ablation_success_rate):>20}"
        )

    print()
    print("Full detection = targeted phenomenon detected by the complete system.")
    print(
        "Ablation success = targeted capability disappears when its "
        "mechanism is disabled."
    )


def main() -> None:
    results = run_ablation_study()
    print_results(results)


if __name__ == "__main__":
    main()
