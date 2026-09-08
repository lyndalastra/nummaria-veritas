"""Define the interface for decomposing claims into atomic propositions."""

from abc import ABC, abstractmethod

from nummaria_veritas.models import Claim, ClaimDecomposition


class ClaimDecomposer(ABC):
    """Interface for decomposing parent claims into atomic propositions."""

    @abstractmethod
    def decompose(self, claim: Claim) -> ClaimDecomposition:
        """Decompose a claim into independently verifiable propositions."""
        ...
