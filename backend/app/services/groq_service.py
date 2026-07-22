"""Synchronous Groq integration boundary for structured complaint AI."""

from __future__ import annotations

import json
import time
from typing import Any

from groq import Groq

from app.core.config import Settings
from app.utils.prompts import EXTRACTION_SYSTEM_PROMPT, RISK_ASSESSMENT_SYSTEM_PROMPT


class GroqService:
    """Own Groq client construction and structured complaint calls."""

    def __init__(self, application_settings: Settings) -> None:
        self.settings = application_settings
        self._client = Groq(api_key=self.settings.groq_api_key) if self.is_configured() else None

    def is_configured(self) -> bool:
        """Report whether a Groq key is available without making a network call."""
        return bool(self.settings.groq_api_key)

    def extract_complaint_fields(self, raw_text: str, current_form_state: dict) -> dict:
        """Extract explicitly supplied complaint fields from source text."""
        payload = {"raw_complaint_text": raw_text, "current_form_state": current_form_state}
        return self._complete(EXTRACTION_SYSTEM_PROMPT, payload, self.settings.model_name)

    def assess_risk(self, fields: dict) -> dict:
        """Assess complaint risk using the reasoning-oriented Groq model."""
        return self._complete(RISK_ASSESSMENT_SYSTEM_PROMPT, fields, "llama-3.3-70b-versatile")

    def _complete(self, system_prompt: str, user_payload: Any, model: str) -> dict:
        if self._client is None:
            raise RuntimeError("GROQ_API_KEY is not configured")

        last_error: Exception | None = None
        for attempt in range(2):
            try:
                response = self._client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": json.dumps(user_payload, default=str)},
                    ],
                    temperature=0,
                    response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content or ""
                try:
                    return self._parse_json(content)
                except json.JSONDecodeError as exc:
                    if attempt == 0:
                        continue
                    raise RuntimeError("Groq returned invalid JSON after one retry") from exc
            except RuntimeError:
                raise
            except Exception as exc:
                last_error = exc
                if attempt == 0:
                    time.sleep(0.25)
                    continue
                raise RuntimeError("Groq request failed after one retry") from exc

        raise RuntimeError("Groq request failed") from last_error

    @staticmethod
    def _parse_json(content: str) -> dict:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
            cleaned = cleaned.removesuffix("```").strip()
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict):
            raise json.JSONDecodeError("Expected a JSON object", cleaned, 0)
        return parsed