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

    if verdicts == {Verdict.SUPPORTED_CLAIM}:
        verdict = Verdict.SUPPORTED_CLAIM

    elif verdicts == {Verdict.INVALID_EVIDENCE}:
        verdict = Verdict.INVALID_EVIDENCE

    elif Verdict.CONTRADICTED_CLAIM in verdicts:
        if len(verdicts) == 1:
            verdict = Verdict.CONTRADICTED_CLAIM
        else:
            verdict = Verdict.PARTIALLY_SUPPORTED_CLAIM

    elif (
        Verdict.PARTIALLY_SUPPORTED_CLAIM in verdicts
        or Verdict.SUPPORTED_CLAIM in verdicts
    ):
        verdict = Verdict.PARTIALLY_SUPPORTED_CLAIM

    elif verdicts == {Verdict.UNSUPPORTED_CLAIM}:
        verdict = Verdict.UNSUPPORTED_CLAIM

    elif verdicts == {Verdict.INSUFFICIENT_EVIDENCE}:
        verdict = Verdict.INSUFFICIENT_EVIDENCE

    else:
        verdict = Verdict.PARTIALLY_SUPPORTED_CLAIM

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
