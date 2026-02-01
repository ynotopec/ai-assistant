from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from ai_assistant.judge import ImprovementJudge, JudgeDecision
from ai_assistant.learning import LearningLog, PerformanceTuner
from ai_assistant.llm import LLMClient
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
        llm_client: Optional[LLMClient] = None,
    ) -> None:
        self.state = AssistantState()
        self.judge = judge or ImprovementJudge()
        self.tuner = tuner or PerformanceTuner()
        self.learning_log = LearningLog()
        self.llm_client = llm_client or LLMClient.from_env()

    def register_tool(self, tool: Tool) -> None:
        self.state.tools[tool.name] = tool

    def ensure_tool(self, task: str) -> Tool:
        tool = self.state.tools.get(task)
        if tool:
            return tool

        def _fallback(payload: str) -> str:
            if self.llm_client:
                system_prompt = (
                    "Tu es un outil spécialisé créé par un assistant IA. "
                    "Ta mission est d'aider l'utilisateur avec précision, "
                    "en limitant les erreurs et en favorisant le bien commun."
                )
                try:
                    return self.llm_client.generate(
                        [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": payload},
                        ]
                    )
                except RuntimeError:
                    pass
            return f"Outil '{task}' généré pour: {payload}"

        tool = SimpleTool(name=task, description="Outil généré automatiquement.", run=_fallback)
        self.register_tool(tool)
        return tool

    def interact(self, user_input: str) -> str:
        response = self._generate_response(user_input)
        errors_detected = self._assess_errors(response)
        interaction = Interaction(
            user_input=user_input,
            assistant_response=response,
            errors_detected=errors_detected,
        )
        self.learn_from_interaction(interaction)
        self._attempt_improvement(interaction)
        return response

    def _generate_response(self, user_input: str) -> str:
        if user_input.startswith("outil:"):
            task = user_input.split(":", 1)[1].strip() or "outil-par-defaut"
            tool = self.ensure_tool(task)
            return tool.run(user_input)
        inferred_tool = self._infer_tool_task(user_input)
        if inferred_tool:
            tool = self.ensure_tool(inferred_tool)
            return tool.run(user_input)
        if self.llm_client:
            return self._generate_with_llm(user_input)
        return (
            "Je n'ai pas de LLM configuré. Définissez OPENAI_API_KEY pour "
            "activer un modèle, ou utilisez le mode outil. "
            "J'apprends de cette interaction et j'améliore mes réponses "
            "pour servir le bien commun."
        )

    def _generate_with_llm(self, user_input: str) -> str:
        system_prompt = (
            "Tu es un assistant IA qui évolue et s'améliore en continu. "
            "Tu apprends de chaque interaction, proposes des améliorations "
            "bénéfiques au bien commun, limites les erreurs, et maximises "
            "l'impact positif. Sois clair, honnête et prudent. "
            f"Niveau de prudence actuel: {self.state.caution_level:.2f}."
        )
        try:
            return self.llm_client.generate(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ]
            )
        except RuntimeError as exc:
            return (
                f"{exc} Utilisez OPENAI_API_KEY/OPENAI_MODEL pour activer "
                "le LLM."
            )

    def learn_from_interaction(self, interaction: Interaction) -> None:
        self.state.knowledge.append(interaction)
        self.learning_log.record(interaction)
        self.state.caution_level = self.tuner.adjust(
            self.state.caution_level, interaction.errors_detected
        )

    def _assess_errors(self, response: str) -> int:
        lowered = response.lower()
        markers = [
            "échec",
            "erreur",
            "réponse llm",
            "je n'ai pas de llm configuré",
        ]
        return 1 if any(marker in lowered for marker in markers) else 0

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

        recent_error_rate = self.learning_log.recent_error_rate()
        if interaction.errors_detected == 0 and recent_error_rate < 0.2:
            return None

        def _change() -> None:
            self.state.caution_level = min(1.0, self.state.caution_level + 0.05)
            if "verification" not in self.state.tools:
                self.register_tool(
                    SimpleTool(
                        name="verification",
                        description="Outil de vérification pour limiter les erreurs.",
                        run=lambda payload: (
                            "Vérifie les faits et sources pour limiter les erreurs. "
                            f"Contexte: {payload}"
                        ),
                    )
                )

        return ImprovementProposal(
            description=(
                "Renforcer la prudence et ajouter une étape de vérification "
                "pour réduire les erreurs."
            ),
            rationale=(
                "Les interactions récentes montrent des signes d'erreur ou "
                "d'incertitude; une vérification améliore la fiabilité."
            ),
            expected_impact=(
                "Moins d'erreurs, meilleure diffusion de la connaissance et "
                "impact positif pour le bien commun."
            ),
            change=_change,
        )

    def _infer_tool_task(self, user_input: str) -> Optional[str]:
        lowered = user_input.lower()
        candidates: List[Tuple[str, str]] = [
            ("résume", "resume"),
            ("résumé", "resume"),
            ("resume", "resume"),
            ("analyse", "analyse"),
            ("analyser", "analyse"),
            ("traduire", "traduction"),
            ("traduction", "traduction"),
            ("plan", "plan"),
            ("checklist", "checklist"),
        ]
        for keyword, tool_name in candidates:
            if keyword in lowered:
                return tool_name
        return None

    def summary(self) -> str:
        return (
            f"Interactions: {len(self.state.knowledge)}, "
            f"Outils: {len(self.state.tools)}, "
            f"Prudence: {self.state.caution_level:.2f}"
        )
