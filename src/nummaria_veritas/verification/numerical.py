"""Extract and compare financial numerical values."""

import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from babel.core import get_global

from nummaria_veritas.models import EvidenceResult

FINANCIAL_SCALE_ALIASES = {
    "k": "thousand",
    "thousand": "thousand",
    "m": "million",
    "mn": "million",
    "mm": "million",
    "million": "million",
    "b": "billion",
    "bn": "billion",
    "billion": "billion",
    "t": "trillion",
    "tn": "trillion",
    "trillion": "trillion",
}

_ISO_CURRENCY_CODES: frozenset[str] = frozenset(get_global("all_currencies").keys())


@dataclass(frozen=True)
class NumericalValue:
    raw: str
    value: Decimal
    is_percentage: bool
    currency: str | None = None
    currency_marker: str | None = None
    scale: str | None = None


class NumericalCheck(str, Enum):
    CONSISTENT = "consistent"
    INCONSISTENT = "inconsistent"
    INSUFFICIENT = "insufficient"


_SCALE_PATTERN = "|".join(
    re.escape(alias)
    for alias in sorted(
        FINANCIAL_SCALE_ALIASES,
        key=len,
        reverse=True,
    )
)

_NUMBER_PATTERN = re.compile(
    rf"""
    (?<![\w.])
    (?P<number>
        [+-]?
        (?:
            \d{{1,3}}(?:,\d{{3}})+
            |
            \d+
        )
        (?:\.\d+)?
    )
    (?P<scale>
        \s*(?:{_SCALE_PATTERN})(?![A-Za-z])
    )?
    (?P<percent>\s*%)?
    """,
    re.IGNORECASE | re.VERBOSE,
)


def normalize_scale(
    scale: str | None,
) -> str | None:
    if scale is None:
        return None

    return FINANCIAL_SCALE_ALIASES.get(scale.strip().lower())


def currencies_are_compatible(
    first: NumericalValue,
    second: NumericalValue,
) -> bool:
    if first.currency is not None and second.currency is not None:
        return first.currency == second.currency

    if first.currency is None and second.currency is None:
        return first.currency_marker == second.currency_marker

    return False


def extract_numerical_values(
    text: str,
) -> list[NumericalValue]:
    values: list[NumericalValue] = []

    for match in _NUMBER_PATTERN.finditer(text):
        number_start = match.start()
        number_end = match.end()

        (
            currency,
            currency_marker,
            raw_start,
            raw_end,
        ) = _find_currency(
            text=text,
            number_start=number_start,
            number_end=number_end,
        )

        if raw_start is None:
            raw_start = number_start

        if raw_end is None:
            raw_end = number_end

        raw = text[raw_start:raw_end].strip()

        number = match.group("number").replace(",", "")

        values.append(
            NumericalValue(
                raw=raw,
                value=Decimal(number),
                is_percentage=(match.group("percent") is not None),
                currency=currency,
                currency_marker=currency_marker,
                scale=normalize_scale(match.group("scale")),
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
            _values_match(
                claim_value=claim_value,
                evidence_value=evidence_value,
            )
            for evidence_value in evidence_values
        )
    ]

    if unmatched_claim_values:
        return NumericalCheck.INCONSISTENT

    return NumericalCheck.CONSISTENT


def _values_match(
    *,
    claim_value: NumericalValue,
    evidence_value: NumericalValue,
) -> bool:
    return (
        claim_value.value == evidence_value.value
        and claim_value.is_percentage == evidence_value.is_percentage
        and currencies_are_compatible(
            claim_value,
            evidence_value,
        )
        and claim_value.scale == evidence_value.scale
    )


def _find_currency(
    *,
    text: str,
    number_start: int,
    number_end: int,
) -> tuple[
    str | None,
    str | None,
    int | None,
    int | None,
]:
    prefix = _find_prefix_currency(
        text=text,
        number_start=number_start,
    )

    if prefix is not None:
        currency, marker, start = prefix

        return (
            currency,
            marker,
            start,
            number_end,
        )

    suffix = _find_suffix_currency(
        text=text,
        number_end=number_end,
    )

    if suffix is not None:
        currency, marker, end = suffix

        return (
            currency,
            marker,
            number_start,
            end,
        )

    return None, None, None, None


def _find_prefix_currency(
    *,
    text: str,
    number_start: int,
) -> (
    tuple[
        str | None,
        str,
        int,
    ]
    | None
):
    position = number_start - 1

    while position >= 0 and text[position].isspace():
        position -= 1

    if position < 0:
        return None

    character = text[position]

    if unicodedata.category(character) == "Sc":
        return (
            None,
            character,
            position,
        )

    token_end = position + 1
    token_start = token_end

    while token_start > 0 and text[token_start - 1].isalpha():
        token_start -= 1

    marker = text[token_start:token_end]

    currency = _resolve_currency_code(marker)

    if currency is None:
        return None

    return (
        currency,
        marker,
        token_start,
    )


def _find_suffix_currency(
    *,
    text: str,
    number_end: int,
) -> (
    tuple[
        str | None,
        str,
        int,
    ]
    | None
):
    position = number_end

    while position < len(text) and text[position].isspace():
        position += 1

    if position >= len(text):
        return None

    character = text[position]

    if unicodedata.category(character) == "Sc":
        return (
            None,
            character,
            position + 1,
        )

    token_end = position

    while token_end < len(text) and text[token_end].isalpha():
        token_end += 1

    marker = text[position:token_end]

    currency = _resolve_currency_code(marker)

    if currency is None:
        return None

    return (
        currency,
        marker,
        token_end,
    )


def _resolve_currency_code(
    marker: str,
) -> str | None:
    candidate = marker.upper()

    if len(candidate) == 3 and candidate in _ISO_CURRENCY_CODES:
        return candidate

    return None
