"""Provide deterministic evidence stance assessments for registered cases."""

from nummaria_veritas.models import (
    AtomicClaim,
    EvidenceAssessment,
    EvidenceResult,
)
from nummaria_veritas.verification.support import EvidenceAssessor


class StaticEvidenceAssessor(EvidenceAssessor):
    def __init__(
        self,
        assessments: dict[str, list[EvidenceAssessment]],
    ) -> None:
        self.assessments = assessments

    def assess(
        self,
        *,
        claim: AtomicClaim,
        evidence: list[EvidenceResult],
    ) -> list[EvidenceAssessment]:
        del evidence

        try:
            return self.assessments[claim.atomic_claim_id]
        except KeyError as exc:
            raise KeyError(
                f"No evidence assessment found for {claim.atomic_claim_id!r}."
            ) from exc
