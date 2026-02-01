from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Interaction:
    user_input: str
    assistant_response: str
    errors_detected: int = 0
