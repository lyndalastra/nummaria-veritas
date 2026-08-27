import json
from pathlib import Path

from nummaria_veritas.models import BenchmarkClaim


def load_benchmark(path: str | Path) -> list[BenchmarkClaim]:
    benchmark_path = Path(path)

    claims: list[BenchmarkClaim] = []

    with benchmark_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                data = json.loads(line)
                claim = BenchmarkClaim.model_validate(data)
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid benchmark entry at line {line_number}: {exc}"
                ) from exc

            claims.append(claim)

    return claims
