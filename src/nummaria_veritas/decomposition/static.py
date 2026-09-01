from nummaria_veritas.decomposition.base import ClaimDecomposer
from nummaria_veritas.models import Claim, ClaimDecomposition


class StaticClaimDecomposer(ClaimDecomposer):
    def __init__(
        self,
        decompositions: dict[str, ClaimDecomposition],
    ) -> None:
        self.decompositions = decompositions

    def decompose(self, claim: Claim) -> ClaimDecomposition:
        try:
            decomposition = self.decompositions[claim.claim_id]
        except KeyError as exc:
            raise KeyError(
                f"No decomposition found for claim {claim.claim_id!r}."
            ) from exc

        if decomposition.parent_claim_id != claim.claim_id:
            raise ValueError("Decomposition parent_claim_id does not match claim_id.")

        return decomposition
