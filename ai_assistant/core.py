from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from ai_assistant.judge import ImprovementJudge, JudgeDecision
from ai_assistant.learning import LearningLog, PerformanceTuner
from ai_assistant.models import Interaction
from ai_assistant.tools import SimpleTool, Tool


@dataclass
class ImprovementProposal:
    description: str
    rationale: str
    expected_impact: str
    change: Callable[[], None]


@dataclass
class AssistantState:
    knowledge: List[Interaction] = field(default_factory=list)
    tools: Dict[str, Tool] = field(default_factory=dict)
    caution_level: float = 0.5
    improvements_applied: List[str] = field(default_factory=list)


class AdaptiveAssistant:
    def __init__(
        self,
        judge: Optional[ImprovementJudge] = None,
        tuner: Optional[PerformanceTuner] = None,
    ) -> None:
        self.state = AssistantState()
        self.judge = judge or ImprovementJudge()
        self.tuner = tuner or PerformanceTuner()
        self.learning_log = LearningLog()

    def register_tool(self, tool: Tool) -> None:
        self.state.tools[tool.name] = tool

    def ensure_tool(self, task: str) -> Tool:
        tool = self.state.tools.get(task)
        if tool:
            return tool

        def _fallback(payload: str) -> str:
            return f"Outil '{task}' généré pour: {payload}"

        tool = SimpleTool(name=task, description="Outil généré automatiquement.", run=_fallback)
        self.register_tool(tool)
        return tool

    def interact(self, user_input: str) -> str:
        response = self._generate_response(user_input)
        interaction = Interaction(user_input=user_input, assistant_response=response)
        self.learn_from_interaction(interaction)
        self._attempt_improvement(interaction)
        return response

    def _generate_response(self, user_input: str) -> str:
        if user_input.startswith("outil:"):
            task = user_input.split(":", 1)[1].strip() or "outil-par-defaut"
            tool = self.ensure_tool(task)
            return tool.run(user_input)
        return (
            "J'apprends de cette interaction et j'améliore mes réponses "
            "pour servir le bien commun."
        )

    def learn_from_interaction(self, interaction: Interaction) -> None:
        self.state.knowledge.append(interaction)
        self.learning_log.record(interaction)
        self.state.caution_level = self.tuner.adjust(
            self.state.caution_level, interaction.errors_detected
        )

    def _attempt_improvement(self, interaction: Interaction) -> Optional[JudgeDecision]:
        proposal = self._propose_improvement(interaction)
        if not proposal:
            return None
        decision = self.judge.evaluate(proposal)
        if decision.approved:
            proposal.change()
            self.state.improvements_applied.append(proposal.description)
        return decision

    def _propose_improvement(self, interaction: Interaction) -> Optional[ImprovementProposal]:
        if not self.state.knowledge:
            return None

        def _change() -> None:
            self.state.caution_level = min(1.0, self.state.caution_level + 0.05)

        return ImprovementProposal(
            description="Augmenter légèrement la prudence pour réduire les erreurs.",
            rationale="Réduction proactive des erreurs après une interaction.",
            expected_impact="Moins d'erreurs et réponses plus fiables.",
            change=_change,
        )

    def summary(self) -> str:
        return (
            f"Interactions: {len(self.state.knowledge)}, "
            f"Outils: {len(self.state.tools)}, "
            f"Prudence: {self.state.caution_level:.2f}"
        )
