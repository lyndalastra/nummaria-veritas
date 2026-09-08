"""Define independently switchable verification ablations."""

from dataclasses import dataclass

from nummaria_veritas.verification.config import VerificationConfig


@dataclass(frozen=True)
class Ablation:
    name: str
    config: VerificationConfig


FULL_SYSTEM = Ablation(
    name="full_system",
    config=VerificationConfig(),
)

NO_TEMPORAL_VALIDITY = Ablation(
    name="without_temporal_validity",
    config=VerificationConfig(
        check_temporal_validity=False,
    ),
)

NO_NUMERICAL_CONSISTENCY = Ablation(
    name="without_numerical_consistency",
    config=VerificationConfig(
        check_numerical_consistency=False,
    ),
)

NO_CAUSAL_CHECK = Ablation(
    name="without_causal_check",
    config=VerificationConfig(
        check_causal_overclaim=False,
    ),
)

NO_EVIDENCE_INDEPENDENCE = Ablation(
    name="without_evidence_independence",
    config=VerificationConfig(
        check_evidence_independence=False,
    ),
)

ABLATIONS = (
    FULL_SYSTEM,
    NO_TEMPORAL_VALIDITY,
    NO_NUMERICAL_CONSISTENCY,
    NO_CAUSAL_CHECK,
    NO_EVIDENCE_INDEPENDENCE,
)
