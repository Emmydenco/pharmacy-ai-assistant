"""Small, explicit policy rules that run before any hosted model call.

These checks are intentionally incomplete keyword/phrase rules. They are a routing
layer for Milestone 1, not a clinical safety system.
"""

from dataclasses import dataclass
import re
from typing import Literal


PolicyCategory = Literal["allowed", "emergency", "pharmacist", "out_of_scope"]


@dataclass(frozen=True)
class PolicyDecision:
    category: PolicyCategory
    message: str


EMERGENCY_PATTERNS = (
    r"can't breathe",
    r"cannot breathe",
    r"trouble breathing",
    r"difficulty breathing",
    r"not breathing",
    r"seizure",
    r"collapsed",
    r"collapse",
    r"unconscious",
    r"not waking",
    r"can't wake",
    r"cannot wake",
    r"overdose",
    r"poisoned",
    r"poisoning",
    r"self[- ]harm",
    r"suicid",
)

PHARMACIST_PATTERNS = (
    r"diagnos",
    r"what disease",
    r"is this cancer",
    r"prescri",
    r"change (my|the) dose",
    r"increase (my|the) dose",
    r"decrease (my|the) dose",
    r"stop taking",
    r"start taking",
    r"switch (my|the) medication",
    r"replace (my|the) medication",
    r"should i take",
    r"personal treatment",
)

OUT_OF_SCOPE_PATTERNS = (
    r"write (a )?(program|code)",
    r"politics",
    r"football score",
    r"tax advice",
    r"relationship advice",
)


def _contains_any(message: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, message, flags=re.IGNORECASE) for pattern in patterns)


def evaluate_message(message: str) -> PolicyDecision:
    """Return the safest simple route for a message before model invocation."""

    normalized = " ".join(message.strip().split())
    if _contains_any(normalized, EMERGENCY_PATTERNS):
        return PolicyDecision(
            category="emergency",
            message=(
                "This may be an emergency. Contact local emergency services immediately "
                "or go to the nearest emergency department. This prototype cannot assess "
                "or manage emergencies."
            ),
        )
    if _contains_any(normalized, PHARMACIST_PATTERNS):
        return PolicyDecision(
            category="pharmacist",
            message=(
                "This question needs a licensed pharmacist or other qualified clinician. "
                "The prototype will not make a diagnosis, prescribe, or recommend a "
                "patient-specific treatment change."
            ),
        )
    if _contains_any(normalized, OUT_OF_SCOPE_PATTERNS):
        return PolicyDecision(
            category="out_of_scope",
            message=(
                "That request is outside this pharmacy information prototype. Please ask "
                "a general, non-diagnostic medication-information question instead."
            ),
        )
    return PolicyDecision(category="allowed", message="")
