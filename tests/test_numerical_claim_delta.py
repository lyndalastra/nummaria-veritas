from datetime import date
from decimal import Decimal

from babel.core import get_global
from hypothesis import assume, given
from hypothesis import strategies as st

from nummaria_veritas.correction.numerical import (
    generate_numerical_claim_delta,
)
from nummaria_veritas.models import (
    Claim,
    ClaimIssue,
    ClaimVerification,
    EvidenceResult,
    Verdict,
)
from nummaria_veritas.verification.numerical import (
    FINANCIAL_SCALE_ALIASES,
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


def _make_claim(
    *,
    formatted_value: str,
) -> Claim:
    return Claim(
        claim_id="claim",
        company="entity",
        text=f"claim {formatted_value}",
        as_of_date=date.min,
    )


def _make_verification(
    *,
    claim_id: str,
    numerical_issue: bool = True,
) -> ClaimVerification:
    return ClaimVerification(
        claim_id=claim_id,
        atomic_results=[],
        verdict=Verdict.CONTRADICTED_CLAIM,
        claim_issues=([ClaimIssue.NUMERICAL_INCONSISTENCY] if numerical_issue else []),
        explanation="verification",
    )


def _make_evidence(
    *,
    formatted_value: str,
) -> EvidenceResult:
    return EvidenceResult(
        chunk_id="chunk",
        document_id="document",
        company="entity",
        document_type="test_document",
        reporting_period="test_period",
        publication_date=date.min,
        page_number=1,
        text=f"evidence {formatted_value}",
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
    claim_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    evidence_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
)
def test_generates_delta_for_plain_numbers(
    claim_value: Decimal,
    evidence_value: Decimal,
) -> None:
    assume(claim_value != evidence_value)

    original_value = str(claim_value)
    revised_value = str(evidence_value)

    claim = _make_claim(
        formatted_value=original_value,
    )

    delta = generate_numerical_claim_delta(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
        ),
        evidence=[
            _make_evidence(
                formatted_value=revised_value,
            )
        ],
    )

    assert delta is not None
    assert delta.original_claim == claim.text
    assert delta.revised_claim is not None
    assert revised_value in delta.revised_claim
    assert delta.changes == [f"{original_value} → {revised_value}"]


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
def test_generates_delta_for_percentages(
    claim_value: Decimal,
    evidence_value: Decimal,
) -> None:
    assume(claim_value != evidence_value)

    original_value = f"{claim_value}%"
    revised_value = f"{evidence_value}%"

    claim = _make_claim(
        formatted_value=original_value,
    )

    delta = generate_numerical_claim_delta(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
        ),
        evidence=[
            _make_evidence(
                formatted_value=revised_value,
            )
        ],
    )

    assert delta is not None
    assert delta.changes == [f"{original_value} → {revised_value}"]


@given(
    claim_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    evidence_value=st.decimals(
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
def test_generates_delta_for_matching_resolved_currency(
    claim_value: Decimal,
    evidence_value: Decimal,
    currency_code: str,
    claim_prefix: bool,
    evidence_prefix: bool,
) -> None:
    assume(claim_value != evidence_value)

    original_value = _format_iso_currency(
        currency_code=currency_code,
        value=claim_value,
        prefix=claim_prefix,
    )

    revised_value = _format_iso_currency(
        currency_code=currency_code,
        value=evidence_value,
        prefix=evidence_prefix,
    )

    claim = _make_claim(
        formatted_value=original_value,
    )

    delta = generate_numerical_claim_delta(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
        ),
        evidence=[
            _make_evidence(
                formatted_value=revised_value,
            )
        ],
    )

    assert delta is not None
    assert delta.changes == [f"{original_value} → {revised_value}"]


@given(
    claim_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    evidence_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    currency_symbol=st.characters(categories=("Sc",)),
    claim_prefix=st.booleans(),
    evidence_prefix=st.booleans(),
)
def test_generates_delta_for_matching_unresolved_currency_marker(
    claim_value: Decimal,
    evidence_value: Decimal,
    currency_symbol: str,
    claim_prefix: bool,
    evidence_prefix: bool,
) -> None:
    assume(claim_value != evidence_value)

    original_value = _format_currency_symbol(
        currency_symbol=currency_symbol,
        value=claim_value,
        prefix=claim_prefix,
    )

    revised_value = _format_currency_symbol(
        currency_symbol=currency_symbol,
        value=evidence_value,
        prefix=evidence_prefix,
    )

    claim = _make_claim(
        formatted_value=original_value,
    )

    delta = generate_numerical_claim_delta(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
        ),
        evidence=[
            _make_evidence(
                formatted_value=revised_value,
            )
        ],
    )

    assert delta is not None
    assert delta.changes == [f"{original_value} → {revised_value}"]


@given(
    claim_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    evidence_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    first_currency=st.sampled_from(ISO_CURRENCY_CODES),
    second_currency=st.sampled_from(ISO_CURRENCY_CODES),
)
def test_different_resolved_currencies_do_not_generate_delta(
    claim_value: Decimal,
    evidence_value: Decimal,
    first_currency: str,
    second_currency: str,
) -> None:
    assume(claim_value != evidence_value)
    assume(first_currency != second_currency)

    claim = _make_claim(
        formatted_value=(f"{first_currency} {claim_value}"),
    )

    delta = generate_numerical_claim_delta(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
        ),
        evidence=[
            _make_evidence(
                formatted_value=(f"{second_currency} {evidence_value}"),
            )
        ],
    )

    assert delta is None


@given(
    claim_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    evidence_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    currency_code=st.sampled_from(ISO_CURRENCY_CODES),
    currency_symbol=st.characters(categories=("Sc",)),
)
def test_resolved_and_unresolved_currency_do_not_generate_delta(
    claim_value: Decimal,
    evidence_value: Decimal,
    currency_code: str,
    currency_symbol: str,
) -> None:
    assume(claim_value != evidence_value)

    claim = _make_claim(
        formatted_value=(f"{currency_code} {claim_value}"),
    )

    delta = generate_numerical_claim_delta(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
        ),
        evidence=[
            _make_evidence(
                formatted_value=(f"{currency_symbol}{evidence_value}"),
            )
        ],
    )

    assert delta is None


@given(
    claim_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    evidence_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    normalized_scale=st.sampled_from(NORMALIZED_SCALES),
    data=st.data(),
)
def test_equivalent_scale_aliases_generate_delta(
    claim_value: Decimal,
    evidence_value: Decimal,
    normalized_scale: str,
    data: st.DataObject,
) -> None:
    assume(claim_value != evidence_value)

    aliases = SCALE_ALIASES_BY_NORMALIZED[normalized_scale]

    claim_scale = data.draw(st.sampled_from(aliases))

    evidence_scale = data.draw(st.sampled_from(aliases))

    original_value = f"{claim_value}{claim_scale}"
    revised_value = f"{evidence_value}{evidence_scale}"

    claim = _make_claim(
        formatted_value=original_value,
    )

    delta = generate_numerical_claim_delta(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
        ),
        evidence=[
            _make_evidence(
                formatted_value=revised_value,
            )
        ],
    )

    assert delta is not None


@given(
    claim_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    evidence_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    first_scale=st.sampled_from(FINANCIAL_SCALES),
    second_scale=st.sampled_from(FINANCIAL_SCALES),
)
def test_different_normalized_scales_do_not_generate_delta(
    claim_value: Decimal,
    evidence_value: Decimal,
    first_scale: str,
    second_scale: str,
) -> None:
    assume(claim_value != evidence_value)

    first_normalized = FINANCIAL_SCALE_ALIASES[first_scale.lower()]

    second_normalized = FINANCIAL_SCALE_ALIASES[second_scale.lower()]

    assume(first_normalized != second_normalized)

    claim = _make_claim(
        formatted_value=(f"{claim_value}{first_scale}"),
    )

    delta = generate_numerical_claim_delta(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
        ),
        evidence=[
            _make_evidence(
                formatted_value=(f"{evidence_value}{second_scale}"),
            )
        ],
    )

    assert delta is None


@given(
    claim_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    evidence_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    currency_code=st.sampled_from(ISO_CURRENCY_CODES),
    normalized_scale=st.sampled_from(NORMALIZED_SCALES),
    data=st.data(),
)
def test_matching_currency_and_equivalent_scale_generate_delta(
    claim_value: Decimal,
    evidence_value: Decimal,
    currency_code: str,
    normalized_scale: str,
    data: st.DataObject,
) -> None:
    assume(claim_value != evidence_value)

    aliases = SCALE_ALIASES_BY_NORMALIZED[normalized_scale]

    claim_scale = data.draw(st.sampled_from(aliases))
    evidence_scale = data.draw(st.sampled_from(aliases))

    original_value = f"{currency_code} {claim_value}{claim_scale}"

    revised_value = f"{currency_code} {evidence_value}{evidence_scale}"

    claim = _make_claim(
        formatted_value=original_value,
    )

    delta = generate_numerical_claim_delta(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
        ),
        evidence=[
            _make_evidence(
                formatted_value=revised_value,
            )
        ],
    )

    assert delta is not None


@given(
    claim_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    evidence_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
)
def test_does_not_generate_delta_without_numerical_issue(
    claim_value: Decimal,
    evidence_value: Decimal,
) -> None:
    claim = _make_claim(
        formatted_value=str(claim_value),
    )

    delta = generate_numerical_claim_delta(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
            numerical_issue=False,
        ),
        evidence=[
            _make_evidence(
                formatted_value=str(evidence_value),
            )
        ],
    )

    assert delta is None


@given(
    claim_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
)
def test_same_value_does_not_generate_delta(
    claim_value: Decimal,
) -> None:
    claim = _make_claim(
        formatted_value=str(claim_value),
    )

    delta = generate_numerical_claim_delta(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
        ),
        evidence=[
            _make_evidence(
                formatted_value=str(claim_value),
            )
        ],
    )

    assert delta is None


@given(
    claim_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    first_evidence_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    second_evidence_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
)
def test_ambiguous_replacements_are_not_guessed(
    claim_value: Decimal,
    first_evidence_value: Decimal,
    second_evidence_value: Decimal,
) -> None:
    assume(claim_value != first_evidence_value)
    assume(claim_value != second_evidence_value)
    assume(first_evidence_value != second_evidence_value)

    claim = _make_claim(
        formatted_value=str(claim_value),
    )

    delta = generate_numerical_claim_delta(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
        ),
        evidence=[
            _make_evidence(
                formatted_value=str(first_evidence_value),
            ),
            _make_evidence(
                formatted_value=str(second_evidence_value),
            ),
        ],
    )

    assert delta is None


@given(
    first_claim_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    second_claim_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
    evidence_value=st.decimals(
        min_value=0,
        max_value=10**12,
        allow_nan=False,
        allow_infinity=False,
        places=4,
    ),
)
def test_multiple_claim_values_are_not_guessed(
    first_claim_value: Decimal,
    second_claim_value: Decimal,
    evidence_value: Decimal,
) -> None:
    claim = Claim(
        claim_id="claim",
        company="entity",
        text=(f"claim {first_claim_value} {second_claim_value}"),
        as_of_date=date.min,
    )

    delta = generate_numerical_claim_delta(
        claim=claim,
        verification=_make_verification(
            claim_id=claim.claim_id,
        ),
        evidence=[
            _make_evidence(
                formatted_value=str(evidence_value),
            )
        ],
    )

    assert delta is None
