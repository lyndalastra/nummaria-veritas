from nummaria_veritas.models import (
    AtomicEvidenceBundle,
    Claim,
    ClaimVerification,
    EvidenceAssessment,
)
from nummaria_veritas.verification.aggregate import (
    aggregate_claim_verification,
)
from nummaria_veritas.verification.config import (
    FULL_VERIFICATION_CONFIG,
    VerificationConfig,
)
from nummaria_veritas.verification.engine import verify_atomic_claim


def verify_claim(
    *,
    claim: Claim,
    atomic_evidence: list[AtomicEvidenceBundle],
    assessments_by_atomic_claim: dict[str, list[EvidenceAssessment]],
    config: VerificationConfig = FULL_VERIFICATION_CONFIG,
) -> ClaimVerification:
    atomic_results = []

    for bundle in atomic_evidence:
        atomic_claim = bundle.atomic_claim

        assessments = assessments_by_atomic_claim.get(
            atomic_claim.atomic_claim_id,
            [],
        )

        atomic_result = verify_atomic_claim(
            claim=claim,
            atomic_claim=atomic_claim,
            assessments=assessments,
            config=config,
        )

        atomic_results.append(atomic_result)

    return aggregate_claim_verification(
        claim_id=claim.claim_id,
        atomic_results=atomic_results,
    )
