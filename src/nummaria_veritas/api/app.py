import logging

from fastapi import FastAPI

from nummaria_veritas.api.logging import configure_logging
from nummaria_veritas.api.models import (
    AtomicVerificationOutput,
    EvidenceOutput,
    HealthResponse,
    VerifyRequest,
    VerifyResponse,
)
from nummaria_veritas.models import (
    AtomicClaim,
    AtomicEvidenceBundle,
    Claim,
    EvidenceAssessment,
    EvidenceResult,
)
from nummaria_veritas.verification.pipeline import verify_claim

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Nummaria Veritas",
    description="Evidence-integrity verification for financial AI claims.",
    version="0.1.0",
)


@app.get(
    "/health",
    response_model=HealthResponse,
)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
    )


@app.post(
    "/verify",
    response_model=VerifyResponse,
)
def verify(request: VerifyRequest) -> VerifyResponse:
    logger.info(
        "Verifying claim claim_id=%s company=%s atomic_claims=%d",
        request.claim_id,
        request.company,
        len(request.atomic_claims),
    )

    claim = Claim(
        claim_id=request.claim_id,
        company=request.company,
        text=request.text,
        as_of_date=request.as_of_date,
        reporting_period=request.reporting_period,
    )

    atomic_evidence: list[AtomicEvidenceBundle] = []
    assessments_by_atomic_claim: dict[
        str,
        list[EvidenceAssessment],
    ] = {}

    for atomic_input in request.atomic_claims:
        atomic_claim = AtomicClaim(
            atomic_claim_id=atomic_input.atomic_claim_id,
            parent_claim_id=request.claim_id,
            text=atomic_input.text,
            proposition_type=atomic_input.proposition_type,
            dependency_ids=atomic_input.dependency_ids,
            is_causal=atomic_input.is_causal,
        )

        evidence_results = [
            EvidenceResult(
                chunk_id=evidence.chunk_id,
                document_id=evidence.document_id,
                company=evidence.company,
                document_type=evidence.document_type,
                reporting_period=evidence.reporting_period,
                publication_date=evidence.publication_date,
                page_number=evidence.page_number,
                text=evidence.text,
                retrieval_score=evidence.retrieval_score,
            )
            for evidence in atomic_input.evidence
        ]

        atomic_evidence.append(
            AtomicEvidenceBundle(
                atomic_claim=atomic_claim,
                evidence=evidence_results,
            )
        )

        assessments_by_atomic_claim[atomic_claim.atomic_claim_id] = [
            EvidenceAssessment(
                evidence=evidence_result,
                stance=evidence_input.stance,
                explanation=evidence_input.assessment_explanation,
            )
            for evidence_input, evidence_result in zip(
                atomic_input.evidence,
                evidence_results,
                strict=True,
            )
        ]

    result = verify_claim(
        claim=claim,
        atomic_evidence=atomic_evidence,
        assessments_by_atomic_claim=assessments_by_atomic_claim,
    )

    logger.info(
        "Verification completed claim_id=%s verdict=%s "
        "claim_issues=%d evidence_issues=%d",
        result.claim_id,
        result.verdict.value,
        len(result.claim_issues),
        len(result.evidence_issues),
    )

    return VerifyResponse(
        claim_id=result.claim_id,
        verdict=result.verdict,
        claim_issues=result.claim_issues,
        evidence_issues=result.evidence_issues,
        explanation=result.explanation,
        atomic_results=[
            AtomicVerificationOutput(
                atomic_claim_id=atomic_result.atomic_claim_id,
                verdict=atomic_result.verdict,
                claim_issues=atomic_result.claim_issues,
                evidence_issues=atomic_result.evidence_issues,
                supporting_evidence=[
                    EvidenceOutput(
                        chunk_id=evidence.chunk_id,
                        document_id=evidence.document_id,
                        page_number=evidence.page_number,
                        text=evidence.text,
                    )
                    for evidence in atomic_result.supporting_evidence
                ],
                contradictory_evidence=[
                    EvidenceOutput(
                        chunk_id=evidence.chunk_id,
                        document_id=evidence.document_id,
                        page_number=evidence.page_number,
                        text=evidence.text,
                    )
                    for evidence in atomic_result.contradictory_evidence
                ],
                explanation=atomic_result.explanation,
            )
            for atomic_result in result.atomic_results
        ],
    )
