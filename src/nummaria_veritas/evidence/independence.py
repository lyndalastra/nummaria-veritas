from dataclasses import dataclass
from datetime import date

from nummaria_veritas.models import EvidenceIssue, EvidenceResult


@dataclass(frozen=True)
class EvidenceCluster:
    cluster_id: str
    evidence: tuple[EvidenceResult, ...]

    @property
    def evidence_count(self) -> int:
        return len(self.evidence)


@dataclass(frozen=True)
class EvidenceIndependenceResult:
    clusters: tuple[EvidenceCluster, ...]
    raw_evidence_count: int
    independent_evidence_count: int
    evidence_issues: tuple[EvidenceIssue, ...]

    @property
    def redundant_evidence_count(self) -> int:
        return self.raw_evidence_count - self.independent_evidence_count


def assess_evidence_independence(
    evidence: list[EvidenceResult],
) -> EvidenceIndependenceResult:
    grouped: dict[
        tuple[str, str, date],
        list[EvidenceResult],
    ] = {}

    for item in evidence:
        provenance_key = (
            item.company,
            item.reporting_period,
            item.publication_date,
        )

        grouped.setdefault(
            provenance_key,
            [],
        ).append(item)

    clusters = tuple(
        EvidenceCluster(
            cluster_id=_build_cluster_id(items),
            evidence=tuple(items),
        )
        for items in grouped.values()
    )

    has_redundancy = any(cluster.evidence_count > 1 for cluster in clusters)

    evidence_issues = (EvidenceIssue.EVIDENCE_REDUNDANCY,) if has_redundancy else ()

    return EvidenceIndependenceResult(
        clusters=clusters,
        raw_evidence_count=len(evidence),
        independent_evidence_count=len(clusters),
        evidence_issues=evidence_issues,
    )


def _build_cluster_id(
    evidence: list[EvidenceResult],
) -> str:
    first = evidence[0]

    return (
        f"{first.company}|{first.reporting_period}|{first.publication_date.isoformat()}"
    )
