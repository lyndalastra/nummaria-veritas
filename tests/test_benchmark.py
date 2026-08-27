from pathlib import Path

from nummaria_veritas.evaluation.benchmark import load_benchmark
from nummaria_veritas.models import Verdict

BENCHMARK_PATH = Path("data/benchmark/claims.jsonl")


def test_benchmark_is_not_empty() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    assert claims


def test_claim_ids_are_unique() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    claim_ids = [claim.claim_id for claim in claims]

    assert len(claim_ids) == len(set(claim_ids))


def test_all_claims_have_company_names() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    assert all(claim.company.strip() for claim in claims)


def test_supported_claims_do_not_have_revisions() -> None:
    claims = load_benchmark(BENCHMARK_PATH)

    supported_claims = [
        claim for claim in claims if claim.expected_verdict == Verdict.SUPPORTED
    ]

    assert all(claim.expected_revised_claim is None for claim in supported_claims)
