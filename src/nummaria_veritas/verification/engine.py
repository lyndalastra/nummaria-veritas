from nummaria_veritas.models import (
    AtomicClaim,
    AtomicVerificationResult,
    Claim,
    ClaimIssue,
    EvidenceAssessment,
    EvidenceIssue,
    EvidenceStance,
    Verdict,
)
from nummaria_veritas.verification.causal import check_causal_overclaim
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
) -> AtomicVerificationResult:
    all_evidence = [assessment.evidence for assessment in assessments]

    evidence_issues = check_temporal_validity(
        claim=claim,
        evidence=all_evidence,
    )

    admissible_assessments = [
        assessment
        for assessment in assessments
        if assessment.evidence.publication_date <= claim.as_of_date
    ]

    admissible_evidence = [assessment.evidence for assessment in admissible_assessments]

    numerical_check = check_numerical_consistency(
        claim_text=atomic_claim.text,
        evidence=admissible_evidence,
    )

    causal_issues = check_causal_overclaim(
        atomic_claim=atomic_claim,
        assessments=admissible_assessments,
    )

    supporting_evidence = [
        assessment.evidence
        for assessment in admissible_assessments
        if assessment.stance == EvidenceStance.SUPPORTS
    ]

    contradictory_evidence = [
        assessment.evidence
        for assessment in admissible_assessments
        if assessment.stance == EvidenceStance.CONTRADICTS
    ]

    claim_issues: list[ClaimIssue] = list(causal_issues)

    if numerical_check == NumericalCheck.INCONSISTENT:
        claim_issues.append(ClaimIssue.NUMERICAL_INCONSISTENCY)

    if contradictory_evidence:
        verdict = Verdict.CONTRADICTED_CLAIM

    elif supporting_evidence and claim_issues:
        verdict = Verdict.PARTIALLY_SUPPORTED_CLAIM

    elif supporting_evidence:
        verdict = Verdict.SUPPORTED_CLAIM

    elif not admissible_evidence:
        verdict = Verdict.INSUFFICIENT_EVIDENCE

    else:
        verdict = Verdict.UNSUPPORTED_CLAIM

    explanation_parts: list[str] = []

    if supporting_evidence:
        explanation_parts.append(
            f"{len(supporting_evidence)} admissible supporting evidence item(s) found."
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
