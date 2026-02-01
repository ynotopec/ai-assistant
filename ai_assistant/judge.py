from __future__ import annotations

from dataclasses import dataclass


@dataclass
class JudgeDecision:
    approved: bool
    reason: str


class ImprovementJudge:
    """Valide les améliorations selon le bien commun et l'impact positif."""

    def evaluate(self, proposal: object) -> JudgeDecision:
        description = getattr(proposal, "description", "")
        rationale = getattr(proposal, "rationale", "")
        expected_impact = getattr(proposal, "expected_impact", "")
        combined = " ".join([description, rationale, expected_impact]).lower()

        if any(term in combined for term in ["nuire", "dommage", "biais"]):
            return JudgeDecision(
                approved=False,
                reason="Rejet: l'amélioration pourrait nuire au bien commun.",
            )

        if "erreur" in combined or "fiable" in combined or "bien commun" in combined:
            return JudgeDecision(
                approved=True,
                reason="Approuvé: amélioration alignée avec l'impact positif.",
            )

        return JudgeDecision(
            approved=False,
            reason="Rejet: impact positif insuffisamment démontré.",
        )
