from datetime import date
from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from nummaria_veritas.models import EvidenceResult
from nummaria_veritas.verification.numerical import (
    NumericalCheck,
    check_numerical_consistency,
    extract_numerical_values,
)


def _make_evidence(text: str) -> EvidenceResult:
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


@given(
    st.integers(
        min_value=0,
        max_value=10**12,
    )
)
def test_integer_values_round_trip(value: int) -> None:
    values = extract_numerical_values(str(value))

    assert len(values) == 1
    assert values[0].value == Decimal(value)
    assert not values[0].is_percentage


@given(
    st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    )
)
def test_decimal_values_round_trip(value: Decimal) -> None:
    values = extract_numerical_values(str(value))

    assert len(values) == 1
    assert values[0].value == value
    assert not values[0].is_percentage


@given(
    st.decimals(
        min_value=0,
        max_value=10**6,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    )
)
def test_percentage_values_round_trip(value: Decimal) -> None:
    values = extract_numerical_values(f"{value}%")

    assert len(values) == 1
    assert values[0].value == value
    assert values[0].is_percentage


@given(
    st.integers(
        min_value=1000,
        max_value=10**12,
    )
)
def test_comma_separated_integer_values_round_trip(value: int) -> None:
    formatted = f"{value:,}"

    values = extract_numerical_values(formatted)

    assert len(values) == 1
    assert values[0].value == Decimal(value)


@given(
    st.integers(
        min_value=0,
        max_value=10**9,
    )
)
def test_numerical_check_accepts_matching_integer(value: int) -> None:
    result = check_numerical_consistency(
        claim_text=str(value),
        evidence=[_make_evidence(str(value))],
    )

    assert result == NumericalCheck.CONSISTENT


@given(
    st.integers(
        min_value=0,
        max_value=10**9,
    ),
    st.integers(
        min_value=0,
        max_value=10**9,
    ),
)
def test_numerical_check_rejects_non_matching_integer(
    claim_value: int,
    evidence_value: int,
) -> None:
    if claim_value == evidence_value:
        return

    result = check_numerical_consistency(
        claim_text=str(claim_value),
        evidence=[_make_evidence(str(evidence_value))],
    )

    assert result == NumericalCheck.INCONSISTENT


@given(
    st.decimals(
        min_value=0,
        max_value=10**6,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    )
)
def test_numerical_check_preserves_percentage_type(
    value: Decimal,
) -> None:
    result = check_numerical_consistency(
        claim_text=f"{value}%",
        evidence=[_make_evidence(str(value))],
    )

    assert result == NumericalCheck.INCONSISTENT


def test_numerical_check_is_insufficient_without_claim_numbers() -> None:
    result = check_numerical_consistency(
        claim_text="no numerical content",
        evidence=[_make_evidence("123")],
    )

    assert result == NumericalCheck.INSUFFICIENT


def test_numerical_check_is_insufficient_without_evidence_numbers() -> None:
    result = check_numerical_consistency(
        claim_text="123",
        evidence=[_make_evidence("no numerical content")],
    )

    assert result == NumericalCheck.INSUFFICIENT
