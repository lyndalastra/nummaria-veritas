from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class Verdict(str, Enum):
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    CONTRADICTED = "contradicted"
    UNSUPPORTED = "unsupported"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class ClaimIssue(str, Enum):
    ANACHRONISTIC_CLAIM = "anachronistic_claim"
    NUMERICAL_INCONSISTENCY = "numerical_inconsistency"
    METRIC_MISMATCH = "metric_mismatch"
    PERIOD_MISMATCH = "period_mismatch"
    ENTITY_SCOPE_MISMATCH = "entity_scope_mismatch"
    FORECAST_AS_FACT = "forecast_as_fact"
    CAUSAL_OVERCLAIM = "causal_overclaim"


class EvidenceIssue(str, Enum):
    TEMPORAL_LEAKAGE = "temporal_leakage"
    EVIDENCE_REDUNDANCY = "evidence_redundancy"
    CONTRADICTORY_EVIDENCE = "contradictory_evidence"


class Document(BaseModel):
    document_id: str
    company: str
    document_type: str
    reporting_period: str
    publication_date: date
    source_path: str


class Evidence(BaseModel):
    document_id: str
    page: int | None = None
    text: str
    relevance_score: float | None = None


class Claim(BaseModel):
    claim_id: str
    company: str
    text: str
    as_of_date: date
    reporting_period: str | None = None


class BenchmarkClaim(Claim):
    expected_verdict: Verdict
    expected_claim_issues: list[ClaimIssue] = Field(default_factory=list)
    expected_revised_claim: str | None = None


class ClaimDelta(BaseModel):
    original_claim: str
    revised_claim: str | None = None
    changes: list[str] = Field(default_factory=list)


class VerificationResult(BaseModel):
    claim_id: str
    verdict: Verdict
    claim_issues: list[ClaimIssue] = Field(default_factory=list)
    evidence_issues: list[EvidenceIssue] = Field(default_factory=list)
    supporting_evidence: list[Evidence] = Field(default_factory=list)
    contradictory_evidence: list[Evidence] = Field(default_factory=list)
    explanation: str
    claim_delta: ClaimDelta | None = None


class Page(BaseModel):
    document_id: str
    page_number: int
    text: str


class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    page_number: int
    chunk_index: int
    text: str


class IngestedChunk(BaseModel):
    chunk_id: str
    document_id: str
    company: str
    document_type: str
    reporting_period: str
    publication_date: date
    page_number: int
    chunk_index: int
    text: str


class EvidenceResult(BaseModel):
    chunk_id: str
    document_id: str
    company: str
    document_type: str
    reporting_period: str
    publication_date: date
    page_number: int
    text: str
    retrieval_score: float


class PropositionType(str, Enum):
    FACT = "fact"
    RELATION = "relation"
    INFERENCE = "inference"


class AtomicClaim(BaseModel):
    atomic_claim_id: str
    parent_claim_id: str
    text: str
    proposition_type: PropositionType
    dependency_ids: list[str] = Field(default_factory=list)


class ClaimDecomposition(BaseModel):
    parent_claim_id: str
    atomic_claims: list[AtomicClaim] = Field(default_factory=list)


class AtomicEvidenceBundle(BaseModel):
    atomic_claim: AtomicClaim
    evidence: list[EvidenceResult] = Field(default_factory=list)


class ClaimEvidenceBundle(BaseModel):
    claim: Claim
    decomposition: ClaimDecomposition
    atomic_evidence: list[AtomicEvidenceBundle] = Field(default_factory=list)
