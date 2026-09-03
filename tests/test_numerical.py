from datetime import date
from decimal import Decimal

from babel.core import get_global
from hypothesis import assume, given
from hypothesis import strategies as st

from nummaria_veritas.models import (
    EvidenceResult,
)
from nummaria_veritas.verification.numerical import (
    FINANCIAL_SCALE_ALIASES,
    NumericalCheck,
    NumericalValue,
    check_numerical_consistency,
    currencies_are_compatible,
    extract_numerical_values,
)

ISO_CURRENCY_CODES = tuple(sorted(get_global("all_currencies").keys()))

FINANCIAL_SCALES = tuple(FINANCIAL_SCALE_ALIASES.keys())

SCALE_ALIASES_BY_NORMALIZED = {
    normalized: tuple(
        sorted(
            alias
            for alias, meaning in FINANCIAL_SCALE_ALIASES.items()
            if meaning == normalized
        )
    )
    for normalized in sorted(set(FINANCIAL_SCALE_ALIASES.values()))
}

NORMALIZED_SCALES = tuple(SCALE_ALIASES_BY_NORMALIZED)


def _make_evidence(
    text: str,
) -> EvidenceResult:
    return EvidenceResult(
        chunk_id="chunk",
        document_id="document",
        company="entity",
        document_type="test_document",
        reporting_period="test_period",
        publication_date=date.min,
        page_number=1,
        text=text,
        retrieval_score=0.0,
    )


def _format_iso_currency(
    *,
    currency_code: str,
    value: Decimal,
    prefix: bool,
) -> str:
    if prefix:
        return f"{currency_code} {value}"

    return f"{value} {currency_code}"


def _format_currency_symbol(
    *,
    currency_symbol: str,
    value: Decimal,
    prefix: bool,
) -> str:
    if prefix:
        return f"{currency_symbol}{value}"

    return f"{value} {currency_symbol}"


@given(
    st.integers(
        min_value=0,
        max_value=10**12,
    )
)
def test_plain_integer_values_round_trip(
    value: int,
) -> None:
    values = extract_numerical_values(str(value))

    assert len(values) == 1
    assert values[0].value == Decimal(value)
    assert not values[0].is_percentage
    assert values[0].currency is None
    assert values[0].currency_marker is None
    assert values[0].scale is None


@given(
    st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    )
)
def test_plain_decimal_values_round_trip(
    value: Decimal,
) -> None:
    values = extract_numerical_values(str(value))

    assert len(values) == 1
    assert values[0].value == value
    assert not values[0].is_percentage
    assert values[0].currency is None
    assert values[0].currency_marker is None
    assert values[0].scale is None


@given(
    st.decimals(
        min_value=0,
        max_value=10**6,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    )
)
def test_percentage_values_round_trip(
    value: Decimal,
) -> None:
    values = extract_numerical_values(f"{value}%")

    assert len(values) == 1
    assert values[0].value == value
    assert values[0].is_percentage
    assert values[0].currency is None
    assert values[0].currency_marker is None


@given(
    value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    currency_code=st.sampled_from(ISO_CURRENCY_CODES),
    prefix=st.booleans(),
)
def test_iso_currency_codes_set_currency_and_marker(
    value: Decimal,
    currency_code: str,
    prefix: bool,
) -> None:
    text = _format_iso_currency(
        currency_code=currency_code,
        value=value,
        prefix=prefix,
    )

    values = extract_numerical_values(text)

    assert len(values) == 1
    assert values[0].value == value
    assert values[0].currency == currency_code
    assert values[0].currency_marker == currency_code


@given(
    value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    currency_symbol=st.characters(categories=("Sc",)),
    prefix=st.booleans(),
)
def test_currency_symbols_set_marker_without_iso_assumption(
    value: Decimal,
    currency_symbol: str,
    prefix: bool,
) -> None:
    text = _format_currency_symbol(
        currency_symbol=currency_symbol,
        value=value,
        prefix=prefix,
    )

    values = extract_numerical_values(text)

    assert len(values) == 1
    assert values[0].value == value
    assert values[0].currency is None
    assert values[0].currency_marker == currency_symbol


@given(
    value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    scale=st.sampled_from(FINANCIAL_SCALES),
)
def test_financial_scales_are_normalized(
    value: Decimal,
    scale: str,
) -> None:
    values = extract_numerical_values(f"{value}{scale}")

    assert len(values) == 1
    assert values[0].value == value
    assert values[0].scale == (FINANCIAL_SCALE_ALIASES[scale.lower()])


@given(
    value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    currency_code=st.sampled_from(ISO_CURRENCY_CODES),
    scale=st.sampled_from(FINANCIAL_SCALES),
    prefix=st.booleans(),
)
def test_currency_and_financial_scale_can_coexist(
    value: Decimal,
    currency_code: str,
    scale: str,
    prefix: bool,
) -> None:
    scaled_value = f"{value}{scale}"

    if prefix:
        text = f"{currency_code} {scaled_value}"
    else:
        text = f"{scaled_value} {currency_code}"

    values = extract_numerical_values(text)

    assert len(values) == 1
    assert values[0].currency == currency_code
    assert values[0].currency_marker == currency_code
    assert values[0].scale == (FINANCIAL_SCALE_ALIASES[scale.lower()])


@given(
    value=st.integers(
        min_value=1000,
        max_value=10**12,
    )
)
def test_comma_separated_values_round_trip(
    value: int,
) -> None:
    values = extract_numerical_values(f"{value:,}")

    assert len(values) == 1
    assert values[0].value == Decimal(value)


@given(
    value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    currency_code=st.sampled_from(ISO_CURRENCY_CODES),
)
def test_matching_resolved_currencies_are_compatible(
    value: Decimal,
    currency_code: str,
) -> None:
    first = NumericalValue(
        raw=f"{currency_code} {value}",
        value=value,
        is_percentage=False,
        currency=currency_code,
        currency_marker=currency_code,
    )

    second = NumericalValue(
        raw=f"{value} {currency_code}",
        value=value,
        is_percentage=False,
        currency=currency_code,
        currency_marker=currency_code,
    )

    assert currencies_are_compatible(
        first,
        second,
    )


@given(
    value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    currency_symbol=st.characters(categories=("Sc",)),
)
def test_matching_unresolved_currency_markers_are_compatible(
    value: Decimal,
    currency_symbol: str,
) -> None:
    first = NumericalValue(
        raw=f"{currency_symbol}{value}",
        value=value,
        is_percentage=False,
        currency=None,
        currency_marker=currency_symbol,
    )

    second = NumericalValue(
        raw=f"{value} {currency_symbol}",
        value=value,
        is_percentage=False,
        currency=None,
        currency_marker=currency_symbol,
    )

    assert currencies_are_compatible(
        first,
        second,
    )


@given(
    value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    first_currency=st.sampled_from(ISO_CURRENCY_CODES),
    second_currency=st.sampled_from(ISO_CURRENCY_CODES),
)
def test_different_resolved_currencies_are_not_compatible(
    value: Decimal,
    first_currency: str,
    second_currency: str,
) -> None:
    assume(first_currency != second_currency)

    first = NumericalValue(
        raw=f"{first_currency} {value}",
        value=value,
        is_percentage=False,
        currency=first_currency,
        currency_marker=first_currency,
    )

    second = NumericalValue(
        raw=f"{second_currency} {value}",
        value=value,
        is_percentage=False,
        currency=second_currency,
        currency_marker=second_currency,
    )

    assert not currencies_are_compatible(
        first,
        second,
    )


@given(
    value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    first_symbol=st.characters(categories=("Sc",)),
    second_symbol=st.characters(categories=("Sc",)),
)
def test_different_unresolved_currency_markers_are_not_compatible(
    value: Decimal,
    first_symbol: str,
    second_symbol: str,
) -> None:
    assume(first_symbol != second_symbol)

    first = NumericalValue(
        raw=f"{first_symbol}{value}",
        value=value,
        is_percentage=False,
        currency=None,
        currency_marker=first_symbol,
    )

    second = NumericalValue(
        raw=f"{second_symbol}{value}",
        value=value,
        is_percentage=False,
        currency=None,
        currency_marker=second_symbol,
    )

    assert not currencies_are_compatible(
        first,
        second,
    )


@given(
    value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    currency_code=st.sampled_from(ISO_CURRENCY_CODES),
    currency_symbol=st.characters(categories=("Sc",)),
)
def test_resolved_and_unresolved_currencies_are_not_assumed_equivalent(
    value: Decimal,
    currency_code: str,
    currency_symbol: str,
) -> None:
    resolved = NumericalValue(
        raw=f"{currency_code} {value}",
        value=value,
        is_percentage=False,
        currency=currency_code,
        currency_marker=currency_code,
    )

    unresolved = NumericalValue(
        raw=f"{currency_symbol}{value}",
        value=value,
        is_percentage=False,
        currency=None,
        currency_marker=currency_symbol,
    )

    assert not currencies_are_compatible(
        resolved,
        unresolved,
    )


@given(
    value=st.decimals(
        min_value=0,
        max_value=10**6,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    )
)
def test_numerical_consistency_accepts_matching_values(
    value: Decimal,
) -> None:
    result = check_numerical_consistency(
        claim_text=f"claim {value}%",
        evidence=[_make_evidence(f"evidence {value}%")],
    )

    assert result == NumericalCheck.CONSISTENT


@given(
    claim_value=st.decimals(
        min_value=0,
        max_value=10**6,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    evidence_value=st.decimals(
        min_value=0,
        max_value=10**6,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
)
def test_numerical_consistency_rejects_different_values(
    claim_value: Decimal,
    evidence_value: Decimal,
) -> None:
    assume(claim_value != evidence_value)

    result = check_numerical_consistency(
        claim_text=(f"claim {claim_value}%"),
        evidence=[_make_evidence(f"evidence {evidence_value}%")],
    )

    assert result == NumericalCheck.INCONSISTENT


@given(
    value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    currency_code=st.sampled_from(ISO_CURRENCY_CODES),
    claim_prefix=st.booleans(),
    evidence_prefix=st.booleans(),
)
def test_numerical_consistency_accepts_same_resolved_currency(
    value: Decimal,
    currency_code: str,
    claim_prefix: bool,
    evidence_prefix: bool,
) -> None:
    claim_value = _format_iso_currency(
        currency_code=currency_code,
        value=value,
        prefix=claim_prefix,
    )

    evidence_value = _format_iso_currency(
        currency_code=currency_code,
        value=value,
        prefix=evidence_prefix,
    )

    result = check_numerical_consistency(
        claim_text=f"claim {claim_value}",
        evidence=[_make_evidence(f"evidence {evidence_value}")],
    )

    assert result == NumericalCheck.CONSISTENT


@given(
    value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    currency_code=st.sampled_from(ISO_CURRENCY_CODES),
    currency_symbol=st.characters(categories=("Sc",)),
)
def test_numerical_consistency_does_not_assume_resolved_and_unresolved_currency_match(
    value: Decimal,
    currency_code: str,
    currency_symbol: str,
) -> None:
    result = check_numerical_consistency(
        claim_text=(f"claim {currency_code} {value}"),
        evidence=[_make_evidence(f"evidence {currency_symbol}{value}")],
    )

    assert result == NumericalCheck.INCONSISTENT


@given(
    value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    normalized_scale=st.sampled_from(NORMALIZED_SCALES),
    data=st.data(),
)
def test_equivalent_scale_aliases_are_numerically_consistent(
    value: Decimal,
    normalized_scale: str,
    data: st.DataObject,
) -> None:
    aliases = SCALE_ALIASES_BY_NORMALIZED[normalized_scale]

    first_alias = data.draw(st.sampled_from(aliases))
    second_alias = data.draw(st.sampled_from(aliases))

    result = check_numerical_consistency(
        claim_text=(f"claim {value}{first_alias}"),
        evidence=[_make_evidence(f"evidence {value}{second_alias}")],
    )

    assert result == NumericalCheck.CONSISTENT


def test_numerical_check_is_insufficient_without_claim_numbers() -> None:
    result = check_numerical_consistency(
        claim_text="claim",
        evidence=[_make_evidence("123")],
    )

    assert result == NumericalCheck.INSUFFICIENT


def test_numerical_check_is_insufficient_without_evidence_numbers() -> None:
    result = check_numerical_consistency(
        claim_text="123",
        evidence=[_make_evidence("evidence")],
    )

    assert result == NumericalCheck.INSUFFICIENT
