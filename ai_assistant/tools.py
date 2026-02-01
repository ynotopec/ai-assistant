from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


class Tool:
    name: str
    description: str

    def run(self, payload: str) -> str:  # pragma: no cover - interface stub
        raise NotImplementedError


@dataclass
class SimpleTool(Tool):
    name: str
    description: str
    run: Callable[[str], str]
