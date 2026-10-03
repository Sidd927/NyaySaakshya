"""Deterministic cross-session reasoning (Phase 5)."""
from nyaysaakshya.crosssession.comparability import (
    Comparability, ComparabilityAssessment, ComparabilityKey, assess, comparable_pair, key_for,
)
from nyaysaakshya.crosssession.baseline import (
    DEFAULT_MAX_HISTORY, DEFAULT_MIN_HISTORY, Baseline, BaselineStatus, FeatureSummary, SessionRef,
    build_baseline, prior_comparable, PopulationIndex,
)
from nyaysaakshya.crosssession.contrast import (
    ContrastResult, ContrastState, evaluate_contrast, find_controls,
)
from nyaysaakshya.crosssession.model import (
    CROSS_ENGINE_VERSION, CROSS_RULES_VERSION, CrossSessionFinding, Deviation,
)
from nyaysaakshya.crosssession.rules import ALL_CROSS_RULES, BLIND_STRIPPING
from nyaysaakshya.crosssession.engine import (
    CrossSessionConfig, CrossSessionEngine, CrossSessionReport,
)

__all__ = [
    "Comparability", "ComparabilityAssessment", "ComparabilityKey", "assess",
    "comparable_pair", "key_for",
    "DEFAULT_MAX_HISTORY", "DEFAULT_MIN_HISTORY", "Baseline", "BaselineStatus", "FeatureSummary", "SessionRef",
    "build_baseline", "prior_comparable", "PopulationIndex",
    "ContrastResult", "ContrastState", "evaluate_contrast", "find_controls",
    "CROSS_ENGINE_VERSION", "CROSS_RULES_VERSION", "CrossSessionFinding", "Deviation",
    "ALL_CROSS_RULES", "BLIND_STRIPPING",
    "CrossSessionConfig", "CrossSessionEngine", "CrossSessionReport",
]
