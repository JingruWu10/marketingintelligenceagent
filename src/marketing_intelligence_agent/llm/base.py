from __future__ import annotations

from typing import Protocol

from ..models import AISynthesis, AnalysisOutput, BusinessContext


class SynthesisProvider(Protocol):
    def synthesize(self, context: BusinessContext, analysis: AnalysisOutput) -> AISynthesis:
        ...
