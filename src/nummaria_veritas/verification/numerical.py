import re
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from nummaria_veritas.models import EvidenceResult


@dataclass(frozen=True)
class NumericalValue:
    raw: str
    value: Decimal
    is_percentage: bool


class NumericalCheck(str, Enum):
    CONSISTENT = "consistent"
    INCONSISTENT = "inconsistent"
    INSUFFICIENT = "insufficient"


_NUMBER_PATTERN = re.compile(
    r"""
    (?<![\w.])
    (?P<number>
        [+-]?
        (?:
            \d{1,3}(?:,\d{3})+
            |
            \d+
        )
        (?:\.\d+)?
    )
    (?P<percent>\s*%)?
    """,
    re.VERBOSE,
)


def extract_numerical_values(text: str) -> list[NumericalValue]:
    values: list[NumericalValue] = []

    for match in _NUMBER_PATTERN.finditer(text):
        raw = match.group(0).strip()
        number = match.group("number").replace(",", "")

        values.append(
            NumericalValue(
                raw=raw,
                value=Decimal(number),
                is_percentage=match.group("percent") is not None,
            )
        )

    return values


def check_numerical_consistency(
    *,
    claim_text: str,
    evidence: list[EvidenceResult],
) -> NumericalCheck:
    claim_values = extract_numerical_values(claim_text)

    if not claim_values:
        return NumericalCheck.INSUFFICIENT

    evidence_values = [
        value for item in evidence for value in extract_numerical_values(item.text)
    ]

    if not evidence_values:
        return NumericalCheck.INSUFFICIENT

    unmatched_claim_values = [
        claim_value
        for claim_value in claim_values
        if not any(
            evidence_value.value == claim_value.value
            and evidence_value.is_percentage == claim_value.is_percentage
            for evidence_value in evidence_values
        )
    ]

    if unmatched_claim_values:
        return NumericalCheck.INCONSISTENT

    return NumericalCheck.CONSISTENT
