from datetime import date

from nummaria_veritas.correction.static import (
    StaticClaimDeltaGenerator,
)
from nummaria_veritas.models import (
    Claim,
    ClaimDelta,
    ClaimVerification,
    CorrectionStatus,
    Verdict,
)


def _make_claim() -> Claim:
    return Claim(
        claim_id="claim",
        company="entity",
        text="claim",
        as_of_date=date.min,
    )


def _make_verification(
    *,
    claim_id: str,
    verdict: Verdict,
) -> ClaimVerification:
    return ClaimVerification(
        claim_id=claim_id,
        atomic_results=[],
        verdict=verdict,
        explanation="verification",
    )


def test_supported_claim_without_delta_requires_no_change() -> None:
    claim = _make_claim()

    generator = StaticClaimDeltaGenerator({})

    result = generator.generate(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
            verdict=Verdict.SUPPORTED_CLAIM,
        ),
    )

    assert result.status == CorrectionStatus.NO_CHANGE_REQUIRED
    assert result.delta is None


def test_unsupported_claim_without_delta_is_missing_correction() -> None:
    claim = _make_claim()

    generator = StaticClaimDeltaGenerator({})

    result = generator.generate(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
            verdict=Verdict.UNSUPPORTED_CLAIM,
        ),
    )

    assert result.status == CorrectionStatus.CORRECTION_MISSING
    assert result.delta is None


def test_supported_claim_with_stored_delta_flags_state_change() -> None:
    claim = _make_claim()

    delta = ClaimDelta(
        original_claim=claim.text,
        revised_claim="revision",
        changes=["change"],
    )

    generator = StaticClaimDeltaGenerator(
        {
            claim.claim_id: delta,
        }
    )

    result = generator.generate(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
            verdict=Verdict.SUPPORTED_CLAIM,
        ),
    )

    assert result.status == CorrectionStatus.CORRECTION_STATE_CHANGED
    assert result.delta == delta


def test_claim_requiring_correction_with_stored_delta_is_available() -> None:
    claim = _make_claim()

    delta = ClaimDelta(
        original_claim=claim.text,
        revised_claim="revision",
        changes=["change"],
    )

    generator = StaticClaimDeltaGenerator(
        {
            claim.claim_id: delta,
        }
    )

    result = generator.generate(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
            verdict=Verdict.CONTRADICTED_CLAIM,
        ),
    )

    assert result.status == CorrectionStatus.CORRECTION_AVAILABLE
    assert result.delta == delta
