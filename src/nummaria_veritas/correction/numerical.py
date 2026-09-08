"""Generate constrained numerical Claim Delta corrections."""

from nummaria_veritas.models import (
    Claim,
    ClaimDelta,
    ClaimIssue,
    ClaimVerification,
    EvidenceResult,
)
from nummaria_veritas.verification.numerical import (
    NumericalValue,
    currencies_are_compatible,
    extract_numerical_values,
)


def generate_numerical_claim_delta(
    *,
    claim: Claim,
    verification: ClaimVerification,
    evidence: list[EvidenceResult],
) -> ClaimDelta | None:
    """Generate a minimal numerical correction when a unique replacement exists."""

    if ClaimIssue.NUMERICAL_INCONSISTENCY not in verification.claim_issues:
        return None

    claim_values = extract_numerical_values(claim.text)

    if len(claim_values) != 1:
        return None

    evidence_values = [
        value for item in evidence for value in extract_numerical_values(item.text)
    ]

    replacement = _find_unique_replacement(
        claim_value=claim_values[0],
        evidence_values=evidence_values,
    )

    if replacement is None:
        return None

    original_value = claim_values[0].raw
    revised_value = replacement.raw

    revised_claim = claim.text.replace(
        original_value,
        revised_value,
        1,
    )

    return ClaimDelta(
        original_claim=claim.text,
        revised_claim=revised_claim,
        changes=[f"{original_value} → {revised_value}"],
    )


def _find_unique_replacement(
    *,
    claim_value: NumericalValue,
    evidence_values: list[NumericalValue],
) -> NumericalValue | None:
    candidates = [
        evidence_value
        for evidence_value in evidence_values
        if _has_compatible_format(
            claim_value=claim_value,
            evidence_value=evidence_value,
        )
        and evidence_value.value != claim_value.value
    ]

    unique_candidates = {
        (
            candidate.value,
            candidate.is_percentage,
            candidate.currency,
            (candidate.currency_marker if candidate.currency is None else None),
            candidate.scale,
        ): candidate
        for candidate in candidates
    }

    if len(unique_candidates) != 1:
        return None

    return next(iter(unique_candidates.values()))


def _has_compatible_format(
    *,
    claim_value: NumericalValue,
    evidence_value: NumericalValue,
) -> bool:
    return (
        claim_value.is_percentage == evidence_value.is_percentage
        and currencies_are_compatible(
            claim_value,
            evidence_value,
        )
        and claim_value.scale == evidence_value.scale
    )
