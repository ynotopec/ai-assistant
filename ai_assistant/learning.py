from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from ai_assistant.models import Interaction


@dataclass
class LearningLog:
    history: List[Interaction] = field(default_factory=list)

    def record(self, interaction: Interaction) -> None:
        self.history.append(interaction)


class PerformanceTuner:
    def adjust(self, caution_level: float, errors_detected: int) -> float:
        if errors_detected > 0:
            return min(1.0, caution_level + 0.1)
        return max(0.1, caution_level - 0.02)
