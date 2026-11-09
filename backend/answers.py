"""Structured generated-answer types used by the governed provider boundary.

The models distinguish conversational wording from explicitly asserted factual claims.
They do not claim that a validated claim is clinically accurate; they only carry the
relationships needed for conservative evidence checks.
"""

from dataclasses import dataclass

from backend.knowledge.models import Citation


@dataclass(frozen=True)
class AnswerClaim:
    """One factual statement with explicit evidence and citation references."""

    claim_id: str
    text: str
    evidence_passage_ids: tuple[str, ...]
    citations: tuple[Citation, ...]


@dataclass(frozen=True)
class StructuredAnswer:
    """Generated wording plus separately represented factual claims."""

    conversational_text: str
    claims: tuple[AnswerClaim, ...] = ()
