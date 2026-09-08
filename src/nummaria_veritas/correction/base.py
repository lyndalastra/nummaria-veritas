"""Define the interface for Claim Delta generation."""

from abc import ABC, abstractmethod

from nummaria_veritas.models import (
    Claim,
    ClaimDeltaRecord,
    ClaimVerification,
)


class ClaimDeltaGenerator(ABC):
    @abstractmethod
    def generate(
        self,
        *,
        claim: Claim,
        verification: ClaimVerification,
    ) -> ClaimDeltaRecord:
        """Determine the correction state and proposed Claim Delta."""
        ...
