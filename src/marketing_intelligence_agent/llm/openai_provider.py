from __future__ import annotations

import os

from openai import OpenAI

from ..models import AISynthesis, AnalysisOutput, BusinessContext
from ..prompts.synthesis import SYSTEM_PROMPT, build_synthesis_input


class OpenAISynthesisProvider:
    """OpenAI-backed synthesis layer using structured outputs.

    The provider receives only trusted business context and deterministic analytical output.
    It does not own metric calculation, statistical validation, or causal claims.
    """

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        client: OpenAI | None = None,
    ) -> None:
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.6")
        self.client = client or OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def synthesize(self, context: BusinessContext, analysis: AnalysisOutput) -> AISynthesis:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_synthesis_input(
                        context.model_dump_json(indent=2),
                        analysis.model_dump_json(indent=2),
                    ),
                },
            ],
            text_format=AISynthesis,
        )

        parsed = response.output_parsed
        if parsed is None:
            raise RuntimeError("OpenAI returned no parsed synthesis output.")
        return parsed
