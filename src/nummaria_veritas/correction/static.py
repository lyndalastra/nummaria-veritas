from nummaria_veritas.correction.base import ClaimDeltaGenerator
from nummaria_veritas.models import (
    Claim,
    ClaimDelta,
    ClaimDeltaRecord,
    ClaimVerification,
    CorrectionStatus,
    Verdict,
)


class StaticClaimDeltaGenerator(ClaimDeltaGenerator):
    def __init__(
        self,
        deltas: dict[str, ClaimDelta],
    ) -> None:
        self.deltas = deltas

    def generate(
        self,
        *,
        claim: Claim,
        verification: ClaimVerification,
    ) -> ClaimDeltaRecord:
        delta = self.deltas.get(claim.claim_id)

        if verification.verdict == Verdict.SUPPORTED_CLAIM:
            if delta is None:
                return ClaimDeltaRecord(
                    claim_id=claim.claim_id,
                    status=CorrectionStatus.NO_CHANGE_REQUIRED,
                    delta=None,
                    explanation=(
                        "The claim is supported and no correction is required."
                    ),
                )

            return ClaimDeltaRecord(
                claim_id=claim.claim_id,
                status=CorrectionStatus.CORRECTION_STATE_CHANGED,
                delta=delta,
                explanation=(
                    "The claim is currently supported, but a stored Claim Delta "
                    "exists. The correction state should be investigated."
                ),
            )

        if delta is None:
            return ClaimDeltaRecord(
                claim_id=claim.claim_id,
                status=CorrectionStatus.CORRECTION_MISSING,
                delta=None,
                explanation=(
                    "The claim requires correction, but no Claim Delta is stored."
                ),
            )

        return ClaimDeltaRecord(
            claim_id=claim.claim_id,
            status=CorrectionStatus.CORRECTION_AVAILABLE,
            delta=delta,
            explanation=(
                "A Claim Delta is available for a claim that requires correction."
            ),
        )
