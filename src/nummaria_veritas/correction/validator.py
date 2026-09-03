from nummaria_veritas.models import (
    Claim,
    ClaimDelta,
    ClaimDeltaValidation,
    DeltaIssue,
)


def validate_claim_delta(
    *,
    claim: Claim,
    delta: ClaimDelta,
    expected_revised_claim: str | None,
) -> ClaimDeltaValidation:
    issues: list[DeltaIssue] = []

    if delta.original_claim != claim.text:
        issues.append(DeltaIssue.ORIGINAL_CLAIM_MISMATCH)

    if delta.revised_claim != expected_revised_claim:
        issues.append(DeltaIssue.REVISED_CLAIM_MISMATCH)

    if not _changes_match_delta(delta):
        issues.append(DeltaIssue.CHANGE_DESCRIPTION_MISMATCH)

    if issues:
        explanation_parts: list[str] = []

        if DeltaIssue.ORIGINAL_CLAIM_MISMATCH in issues:
            explanation_parts.append(
                "The original claim recorded in the Claim Delta does not "
                "match the provided claim."
            )

        if DeltaIssue.REVISED_CLAIM_MISMATCH in issues:
            explanation_parts.append(
                "The revised claim recorded in the Claim Delta does not "
                "match the expected evidence-backed revision."
            )

        if DeltaIssue.CHANGE_DESCRIPTION_MISMATCH in issues:
            explanation_parts.append(
                "The recorded changes do not correspond to the transformation "
                "between the original and revised claims."
            )

        return ClaimDeltaValidation(
            is_valid=False,
            issues=issues,
            explanation=" ".join(explanation_parts),
        )

    return ClaimDeltaValidation(
        is_valid=True,
        issues=[],
        explanation=(
            "The Claim Delta matches the original claim, expected revision, "
            "and recorded transformation."
        ),
    )


def _changes_match_delta(
    delta: ClaimDelta,
) -> bool:
    if delta.revised_claim is None:
        return delta.changes == []

    if not delta.changes:
        return False

    for change in delta.changes:
        if "→" not in change:
            return False

        original_part, revised_part = [
            part.strip() for part in change.split("→", maxsplit=1)
        ]

        if original_part not in delta.original_claim:
            return False

        if revised_part not in delta.revised_claim:
            return False

    return True
