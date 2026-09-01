from abc import ABC, abstractmethod

from nummaria_veritas.models import Claim, ClaimDecomposition


class ClaimDecomposer(ABC):
    @abstractmethod
    def decompose(self, claim: Claim) -> ClaimDecomposition:
        """Decompose a claim into independently verifiable propositions."""
        ...
