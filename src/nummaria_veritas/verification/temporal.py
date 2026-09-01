from nummaria_veritas.models import (
    Claim,
    EvidenceIssue,
    EvidenceResult,
)


def check_temporal_validity(
    *,
    claim: Claim,
    evidence: list[EvidenceResult],
) -> list[EvidenceIssue]:
    has_future_evidence = any(
        item.publication_date > claim.as_of_date for item in evidence
    )

    if has_future_evidence:
        return [EvidenceIssue.TEMPORAL_LEAKAGE]

    return []
