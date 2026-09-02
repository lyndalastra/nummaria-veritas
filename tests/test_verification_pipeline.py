from datetime import date

from nummaria_veritas.models import (
    AtomicClaim,
    AtomicEvidenceBundle,
    Claim,
    EvidenceAssessment,
    EvidenceResult,
    EvidenceStance,
    PropositionType,
    Verdict,
)
from nummaria_veritas.verification.pipeline import verify_claim


def test_verification_pipeline_returns_parent_verdict() -> None:
    claim = Claim(
        claim_id="parent",
        company="entity",
        text="claim",
        as_of_date=date.min,
    )

    atomic_claims = [
        AtomicClaim(
            atomic_claim_id=f"{claim.claim_id}_{index}",
            parent_claim_id=claim.claim_id,
            text=f"atomic_claim_{index}",
            proposition_type=PropositionType.FACT,
        )
        for index in range(2)
    ]

    evidence = [
        EvidenceResult(
            chunk_id=f"chunk_{index}",
            document_id=f"document_{index}",
            company=claim.company,
            document_type="test_document",
            reporting_period=f"period_{index}",
            publication_date=claim.as_of_date,
            page_number=index + 1,
            text=f"evidence_{index}",
            retrieval_score=0.0,
        )
        for index in range(len(atomic_claims))
    ]

    atomic_evidence = [
        AtomicEvidenceBundle(
            atomic_claim=atomic_claim,
            evidence=[evidence_item],
        )
        for atomic_claim, evidence_item in zip(
            atomic_claims,
            evidence,
            strict=True,
        )
    ]

    assessments_by_atomic_claim = {
        atomic_claim.atomic_claim_id: [
            EvidenceAssessment(
                evidence=evidence_item,
                stance=EvidenceStance.SUPPORTS,
                explanation="The evidence supports the proposition.",
            )
        ]
        for atomic_claim, evidence_item in zip(
            atomic_claims,
            evidence,
            strict=True,
        )
    }

    result = verify_claim(
        claim=claim,
        atomic_evidence=atomic_evidence,
        assessments_by_atomic_claim=assessments_by_atomic_claim,
    )

    assert result.claim_id == claim.claim_id
    assert len(result.atomic_results) == len(atomic_claims)
    assert result.verdict == Verdict.SUPPORTED
