from nummaria_veritas.models import (
    AtomicVerificationResult,
    ClaimVerification,
    Verdict,
)


def aggregate_claim_verification(
    *,
    claim_id: str,
    atomic_results: list[AtomicVerificationResult],
) -> ClaimVerification:
    if not atomic_results:
        return ClaimVerification(
            claim_id=claim_id,
            atomic_results=[],
            verdict=Verdict.INSUFFICIENT_EVIDENCE,
            explanation=("No atomic verification results are available for the claim."),
        )

    verdicts = {result.verdict for result in atomic_results}

    if verdicts == {Verdict.SUPPORTED}:
        verdict = Verdict.SUPPORTED

    elif Verdict.CONTRADICTED in verdicts:
        if len(verdicts) == 1:
            verdict = Verdict.CONTRADICTED
        else:
            verdict = Verdict.PARTIALLY_SUPPORTED

    elif Verdict.PARTIALLY_SUPPORTED in verdicts or Verdict.SUPPORTED in verdicts:
        verdict = Verdict.PARTIALLY_SUPPORTED

    elif verdicts == {Verdict.UNSUPPORTED}:
        verdict = Verdict.UNSUPPORTED

    elif verdicts == {Verdict.INSUFFICIENT_EVIDENCE}:
        verdict = Verdict.INSUFFICIENT_EVIDENCE

    else:
        verdict = Verdict.PARTIALLY_SUPPORTED

    claim_issues = list(
        dict.fromkeys(
            issue for result in atomic_results for issue in result.claim_issues
        )
    )

    evidence_issues = list(
        dict.fromkeys(
            issue for result in atomic_results for issue in result.evidence_issues
        )
    )

    explanation_parts = [
        f"{result.atomic_claim_id}: {result.verdict.value}."
        for result in atomic_results
    ]

    return ClaimVerification(
        claim_id=claim_id,
        atomic_results=atomic_results,
        verdict=verdict,
        claim_issues=claim_issues,
        evidence_issues=evidence_issues,
        explanation=" ".join(explanation_parts),
    )
