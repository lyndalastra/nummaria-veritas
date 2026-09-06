from dataclasses import dataclass


@dataclass(frozen=True)
class VerificationConfig:
    check_temporal_validity: bool = True
    check_numerical_consistency: bool = True
    check_causal_overclaim: bool = True
    check_evidence_independence: bool = True


FULL_VERIFICATION_CONFIG = VerificationConfig()
