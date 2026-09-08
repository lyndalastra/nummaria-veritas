"""Define request and response models for the verification API."""

from datetime import date

from pydantic import BaseModel, Field

from nummaria_veritas.models import (
    ClaimIssue,
    EvidenceIssue,
    EvidenceStance,
    PropositionType,
    Verdict,
)


class EvidenceInput(BaseModel):
    chunk_id: str
    document_id: str
    company: str
    document_type: str
    reporting_period: str
    publication_date: date
    page_number: int
    text: str
    retrieval_score: float | None = None
    stance: EvidenceStance
    assessment_explanation: str


class AtomicClaimInput(BaseModel):
    atomic_claim_id: str
    text: str
    proposition_type: PropositionType
    dependency_ids: list[str] = Field(default_factory=list)
    is_causal: bool = False
    evidence: list[EvidenceInput] = Field(default_factory=list)


class VerifyRequest(BaseModel):
    claim_id: str
    company: str
    text: str
    as_of_date: date
    reporting_period: str | None = None
    atomic_claims: list[AtomicClaimInput]


class EvidenceOutput(BaseModel):
    chunk_id: str
    document_id: str
    page_number: int
    text: str


class AtomicVerificationOutput(BaseModel):
    atomic_claim_id: str
    verdict: Verdict
    claim_issues: list[ClaimIssue]
    evidence_issues: list[EvidenceIssue]
    supporting_evidence: list[EvidenceOutput]
    contradictory_evidence: list[EvidenceOutput]
    explanation: str


class VerifyResponse(BaseModel):
    claim_id: str
    verdict: Verdict
    claim_issues: list[ClaimIssue]
    evidence_issues: list[EvidenceIssue]
    explanation: str
    atomic_results: list[AtomicVerificationOutput]


class HealthResponse(BaseModel):
    status: str
