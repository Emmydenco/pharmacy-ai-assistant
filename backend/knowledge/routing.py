"""Question-category routing to governed source categories."""

from dataclasses import dataclass

from backend.knowledge.models import SourceRecord
from backend.knowledge.source_registry import SourceRegistry


@dataclass(frozen=True)
class SourceRoutingRule:
    question_category: str
    source_categories: tuple[str, ...]
    rationale: str


class SourceRouter:
    """Maps question categories to source categories without granting answer permission."""

    DEFAULT_RULES = (
        SourceRoutingRule(
            question_category="nigerian_drug_registration_recalls_alerts",
            source_categories=("nigerian_regulatory",),
            rationale="Use the Nigerian regulator for Nigerian product status and safety notices.",
        ),
        SourceRoutingRule(
            question_category="nigerian_pharmacy_practice_regulation",
            source_categories=("nigerian_pharmacy_regulation",),
            rationale="Use the Nigerian pharmacy regulator for practice and licensing matters.",
        ),
        SourceRoutingRule(
            question_category="nigerian_national_health_policy",
            source_categories=("nigerian_health_policy",),
            rationale="Use the Nigerian ministry for national policy context.",
        ),
        SourceRoutingRule(
            question_category="international_public_health_recommendations",
            source_categories=("international_public_health",),
            rationale="Use an international public-health authority within its stated scope.",
        ),
        SourceRoutingRule(
            question_category="international_regulatory_product_information",
            source_categories=("international_regulatory_product_information",),
            rationale="Use the jurisdiction-specific regulator and identify that jurisdiction.",
        ),
        SourceRoutingRule(
            question_category="exact_product_information",
            source_categories=("product_information", "manufacturer_product_information"),
            rationale="Match exact product, market, formulation, and document revision first.",
        ),
        SourceRoutingRule(
            question_category="general_patient_education",
            source_categories=("patient_information",),
            rationale="Use an approved patient-information source for general education only.",
        ),
    )

    def __init__(self, rules: tuple[SourceRoutingRule, ...] | None = None) -> None:
        selected = rules or self.DEFAULT_RULES
        if not selected:
            raise ValueError("At least one routing rule is required")
        self._rules = {rule.question_category: rule for rule in selected}

    def rule_for(self, question_category: str) -> SourceRoutingRule:
        try:
            return self._rules[question_category]
        except KeyError as exc:
            raise ValueError(f"No routing rule for question category: {question_category}") from exc

    def all_rules(self) -> tuple[SourceRoutingRule, ...]:
        return tuple(self._rules.values())

    def route(
        self,
        question_category: str,
        registry: SourceRegistry,
        *,
        as_of=None,
    ) -> tuple[SourceRecord, ...]:
        rule = self.rule_for(question_category)
        return tuple(
            source
            for source in registry.all_sources()
            if source.source_category in rule.source_categories
            and registry.can_link(source.source_id, as_of=as_of)
        )
