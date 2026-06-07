from __future__ import annotations

from typing import Any


class ModelBackend:
    def complete_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class HeuristicBackend(ModelBackend):
    def complete_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        return {
            "backend": "heuristic",
            "prompt": prompt,
            "schema_title": schema.get("title"),
        }


class OpenAICompatibleBackend(ModelBackend):
    def complete_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(
            "OpenAI-compatible backend is a future v0.1+ stub and is not configured."
        )

