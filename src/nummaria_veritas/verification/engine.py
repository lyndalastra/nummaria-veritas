from nummaria_veritas.evidence.independence import (
    EvidenceIndependenceResult,
    assess_evidence_independence,
)
from nummaria_veritas.models import (
    AtomicClaim,
    AtomicVerificationResult,
    Claim,
    ClaimIssue,
    EvidenceAssessment,
    EvidenceIssue,
    EvidenceResult,
    EvidenceStance,
    Verdict,
)
from nummaria_veritas.verification.causal import check_causal_overclaim
from nummaria_veritas.verification.config import (
    FULL_VERIFICATION_CONFIG,
    VerificationConfig,
)
from nummaria_veritas.verification.numerical import (
    NumericalCheck,
    check_numerical_consistency,
)
from nummaria_veritas.verification.temporal import (
    check_temporal_validity,
)


def verify_atomic_claim(
    *,
    claim: Claim,
    atomic_claim: AtomicClaim,
    assessments: list[EvidenceAssessment],
    config: VerificationConfig = FULL_VERIFICATION_CONFIG,
) -> AtomicVerificationResult:
    all_evidence = [assessment.evidence for assessment in assessments]

    if config.check_temporal_validity:
        evidence_issues = check_temporal_validity(
            claim=claim,
            evidence=all_evidence,
        )

        admissible_assessments = [
            assessment
            for assessment in assessments
            if assessment.evidence.publication_date <= claim.as_of_date
        ]
    else:
        evidence_issues = []
        admissible_assessments = list(assessments)

    admissible_evidence = [assessment.evidence for assessment in admissible_assessments]

    numerical_check = (
        check_numerical_consistency(
            claim_text=atomic_claim.text,
            evidence=admissible_evidence,
        )
        if config.check_numerical_consistency
        else NumericalCheck.CONSISTENT
    )

    causal_issues = (
        check_causal_overclaim(
            atomic_claim=atomic_claim,
            assessments=admissible_assessments,
        )
        if config.check_causal_overclaim
        else []
    )

    fully_supporting_evidence = [
        assessment.evidence
        for assessment in admissible_assessments
        if assessment.stance == EvidenceStance.SUPPORTS
    ]

    partially_supporting_evidence = [
        assessment.evidence
        for assessment in admissible_assessments
        if assessment.stance == EvidenceStance.PARTIALLY_SUPPORTS
    ]

    supporting_evidence = [
        *fully_supporting_evidence,
        *partially_supporting_evidence,
    ]

    contradictory_evidence = [
        assessment.evidence
        for assessment in admissible_assessments
        if assessment.stance == EvidenceStance.CONTRADICTS
    ]

    independence_result = _assess_independence(
        supporting_evidence=supporting_evidence,
        config=config,
    )

    evidence_issues.extend(
        issue
        for issue in independence_result.evidence_issues
        if issue not in evidence_issues
    )

    claim_issues: list[ClaimIssue] = list(causal_issues)

    if numerical_check == NumericalCheck.INCONSISTENT:
        claim_issues.append(ClaimIssue.NUMERICAL_INCONSISTENCY)

    if contradictory_evidence:
        verdict = Verdict.CONTRADICTED_CLAIM

    elif partially_supporting_evidence or fully_supporting_evidence and claim_issues:
        verdict = Verdict.PARTIALLY_SUPPORTED_CLAIM

    elif fully_supporting_evidence:
        verdict = Verdict.SUPPORTED_CLAIM

    elif not admissible_evidence:
        verdict = Verdict.INSUFFICIENT_EVIDENCE

    else:
        verdict = Verdict.UNSUPPORTED_CLAIM

    explanation_parts: list[str] = []

    if fully_supporting_evidence:
        explanation_parts.append(
            f"{len(fully_supporting_evidence)} admissible fully supporting "
            "evidence item(s) found."
        )

    if partially_supporting_evidence:
        explanation_parts.append(
            f"{len(partially_supporting_evidence)} admissible partially "
            "supporting evidence item(s) found."
        )

    if contradictory_evidence:
        explanation_parts.append(
            f"{len(contradictory_evidence)} admissible contradictory "
            "evidence item(s) found."
        )

    if numerical_check == NumericalCheck.INCONSISTENT:
        explanation_parts.append(
            "The numerical values asserted in the claim are not fully "
            "consistent with the admissible evidence."
        )

    if ClaimIssue.CAUSAL_OVERCLAIM in claim_issues:
        explanation_parts.append(
            "The proposition asserts a causal relationship that is not "
            "established by the admissible evidence."
        )

    if EvidenceIssue.TEMPORAL_LEAKAGE in evidence_issues:
        future_count = len(assessments) - len(admissible_assessments)

        explanation_parts.append(
            f"{future_count} evidence item(s) were excluded because "
            "they were published after the claim's as-of date."
        )

    if EvidenceIssue.EVIDENCE_REDUNDANCY in evidence_issues:
        explanation_parts.append(
            f"{independence_result.raw_evidence_count} supporting "
            "evidence item(s) represent "
            f"{independence_result.independent_evidence_count} "
            "independent evidence source(s)."
        )

    if not admissible_evidence:
        explanation_parts.append(
            "No admissible evidence is available to establish the proposition."
        )

    elif not supporting_evidence and not contradictory_evidence:
        explanation_parts.append(
            "The admissible evidence does not support or contradict the proposition."
        )

    return AtomicVerificationResult(
        atomic_claim_id=atomic_claim.atomic_claim_id,
        verdict=verdict,
        claim_issues=claim_issues,
        evidence_issues=evidence_issues,
        supporting_evidence=supporting_evidence,
        contradictory_evidence=contradictory_evidence,
        explanation=" ".join(explanation_parts),
    )


def _assess_independence(
    *,
    supporting_evidence: list[EvidenceResult],
    config: VerificationConfig,
) -> EvidenceIndependenceResult:
    if config.check_evidence_independence:
        return assess_evidence_independence(supporting_evidence)

    return EvidenceIndependenceResult(
        clusters=(),
        raw_evidence_count=len(supporting_evidence),
        independent_evidence_count=len(supporting_evidence),
        evidence_issues=(),
    )
