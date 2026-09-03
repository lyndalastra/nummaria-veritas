from datetime import date

from nummaria_veritas.correction.validator import validate_claim_delta
from nummaria_veritas.models import (
    Claim,
    ClaimDelta,
    DeltaIssue,
)


def _make_claim() -> Claim:
    return Claim(
        claim_id="claim",
        company="entity",
        text="claim",
        as_of_date=date.min,
    )


def test_valid_delta_passes_validation() -> None:
    claim = _make_claim()

    revised_claim = "revision"

    delta = ClaimDelta(
        original_claim=claim.text,
        revised_claim=revised_claim,
        changes=[f"{claim.text} → {revised_claim}"],
    )

    result = validate_claim_delta(
        claim=claim,
        delta=delta,
        expected_revised_claim=revised_claim,
    )

    assert result.is_valid
    assert result.issues == []


def test_original_claim_mismatch_is_flagged() -> None:
    claim = _make_claim()

    revised_claim = "revision"

    delta = ClaimDelta(
        original_claim="different_claim",
        revised_claim=revised_claim,
        changes=[],
    )

    result = validate_claim_delta(
        claim=claim,
        delta=delta,
        expected_revised_claim=revised_claim,
    )

    assert not result.is_valid
    assert DeltaIssue.ORIGINAL_CLAIM_MISMATCH in result.issues


def test_revised_claim_mismatch_is_flagged() -> None:
    claim = _make_claim()

    expected_revision = "expected_revision"

    delta = ClaimDelta(
        original_claim=claim.text,
        revised_claim="different_revision",
        changes=[],
    )

    result = validate_claim_delta(
        claim=claim,
        delta=delta,
        expected_revised_claim=expected_revision,
    )

    assert not result.is_valid
    assert DeltaIssue.REVISED_CLAIM_MISMATCH in result.issues


def test_both_delta_sides_can_fail_independently() -> None:
    claim = _make_claim()

    delta = ClaimDelta(
        original_claim="different_claim",
        revised_claim="different_revision",
        changes=[],
    )

    result = validate_claim_delta(
        claim=claim,
        delta=delta,
        expected_revised_claim="expected_revision",
    )

    assert not result.is_valid
    assert DeltaIssue.ORIGINAL_CLAIM_MISMATCH in result.issues
    assert DeltaIssue.REVISED_CLAIM_MISMATCH in result.issues


def test_no_revision_passes_when_no_revision_is_expected() -> None:
    claim = _make_claim()

    delta = ClaimDelta(
        original_claim=claim.text,
        revised_claim=None,
        changes=[],
    )

    result = validate_claim_delta(
        claim=claim,
        delta=delta,
        expected_revised_claim=None,
    )

    assert result.is_valid
    assert result.issues == []


def test_change_description_mismatch_is_flagged() -> None:
    claim = _make_claim()

    delta = ClaimDelta(
        original_claim=claim.text,
        revised_claim="revised_claim",
        changes=["wrong_original → revised_claim"],
    )

    result = validate_claim_delta(
        claim=claim,
        delta=delta,
        expected_revised_claim="revised_claim",
    )

    assert not result.is_valid
    assert DeltaIssue.CHANGE_DESCRIPTION_MISMATCH in result.issues


def test_missing_change_is_flagged_when_revision_exists() -> None:
    claim = _make_claim()

    delta = ClaimDelta(
        original_claim=claim.text,
        revised_claim="revised_claim",
        changes=[],
    )

    result = validate_claim_delta(
        claim=claim,
        delta=delta,
        expected_revised_claim="revised_claim",
    )

    assert not result.is_valid
    assert DeltaIssue.CHANGE_DESCRIPTION_MISMATCH in result.issues


def test_no_change_description_is_valid_when_no_revision_exists() -> None:
    claim = _make_claim()

    delta = ClaimDelta(
        original_claim=claim.text,
        revised_claim=None,
        changes=[],
    )

    result = validate_claim_delta(
        claim=claim,
        delta=delta,
        expected_revised_claim=None,
    )

    assert result.is_valid
