from abc import ABC, abstractmethod

from nummaria_veritas.models import (
    AtomicClaim,
    EvidenceAssessment,
    EvidenceResult,
)


class EvidenceAssessor(ABC):
    @abstractmethod
    def assess(
        self,
        *,
        claim: AtomicClaim,
        evidence: list[EvidenceResult],
    ) -> list[EvidenceAssessment]:
        """Assess how each evidence item relates to an atomic claim."""
        ...
