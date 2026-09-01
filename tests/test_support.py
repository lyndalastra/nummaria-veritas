from datetime import date

import pytest

from nummaria_veritas.models import (
    AtomicClaim,
    EvidenceAssessment,
    EvidenceResult,
    EvidenceStance,
    PropositionType,
)
from nummaria_veritas.verification.static_support import (
    StaticEvidenceAssessor,
)


def _make_claim() -> AtomicClaim:
    return AtomicClaim(
        atomic_claim_id="atomic",
        parent_claim_id="parent",
        text="Test proposition.",
        proposition_type=PropositionType.FACT,
    )


def _make_evidence() -> EvidenceResult:
    return EvidenceResult(
        chunk_id="chunk",
        document_id="document",
        company="entity",
        document_type="test_document",
        reporting_period="test_period",
        publication_date=date.min,
        page_number=1,
        text="Test evidence.",
        retrieval_score=0.0,
    )


def test_static_assessor_returns_registered_assessments() -> None:
    claim = _make_claim()
    evidence = _make_evidence()

    expected = [
        EvidenceAssessment(
            evidence=evidence,
            stance=EvidenceStance.SUPPORTS,
            explanation="Evidence supports the proposition.",
        )
    ]

    assessor = StaticEvidenceAssessor({claim.atomic_claim_id: expected})

    result = assessor.assess(
        claim=claim,
        evidence=[evidence],
    )

    assert result == expected


def test_static_assessor_rejects_unknown_claim() -> None:
    claim = _make_claim()

    assessor = StaticEvidenceAssessor({})

    with pytest.raises(KeyError):
        assessor.assess(
            claim=claim,
            evidence=[],
        )
