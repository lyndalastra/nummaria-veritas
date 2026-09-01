from datetime import date

import pytest

from nummaria_veritas.decomposition.static import StaticClaimDecomposer
from nummaria_veritas.models import (
    AtomicClaim,
    Claim,
    ClaimDecomposition,
    PropositionType,
)


def _make_claim() -> Claim:
    return Claim(
        claim_id="parent",
        company="entity",
        text="Composite financial statement.",
        as_of_date=date.min,
        reporting_period=None,
    )


def _make_decomposition(
    parent_claim_id: str,
) -> ClaimDecomposition:
    atomic_claim = AtomicClaim(
        atomic_claim_id=f"{parent_claim_id}_a",
        parent_claim_id=parent_claim_id,
        text="Atomic proposition.",
        proposition_type=PropositionType.FACT,
    )

    return ClaimDecomposition(
        parent_claim_id=parent_claim_id,
        atomic_claims=[atomic_claim],
    )


def test_static_decomposer_returns_registered_decomposition() -> None:
    claim = _make_claim()
    decomposition = _make_decomposition(claim.claim_id)

    decomposer = StaticClaimDecomposer({claim.claim_id: decomposition})

    result = decomposer.decompose(claim)

    assert result == decomposition


def test_static_decomposer_rejects_missing_claim() -> None:
    claim = _make_claim()

    decomposer = StaticClaimDecomposer({})

    with pytest.raises(KeyError):
        decomposer.decompose(claim)


def test_static_decomposer_rejects_parent_mismatch() -> None:
    claim = _make_claim()
    decomposition = _make_decomposition("different_parent")

    decomposer = StaticClaimDecomposer({claim.claim_id: decomposition})

    with pytest.raises(
        ValueError,
        match="parent_claim_id does not match claim_id",
    ):
        decomposer.decompose(claim)
