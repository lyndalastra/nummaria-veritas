from nummaria_veritas.models import (
    AtomicClaim,
    ClaimIssue,
    EvidenceAssessment,
    EvidenceStance,
)


def check_causal_overclaim(
    *,
    atomic_claim: AtomicClaim,
    assessments: list[EvidenceAssessment],
) -> list[ClaimIssue]:
    if not atomic_claim.is_causal:
        return []

    has_causal_support = any(
        assessment.stance == EvidenceStance.SUPPORTS for assessment in assessments
    )

    if has_causal_support:
        return []

    return [ClaimIssue.CAUSAL_OVERCLAIM]
