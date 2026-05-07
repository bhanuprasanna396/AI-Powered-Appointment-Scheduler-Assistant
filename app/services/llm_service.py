import json
import logging
import os
import re
from typing import Any, Dict, Optional

from openai import OpenAI

from app.utils.retry import with_retry

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout_seconds = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "6"))
        self._client: Optional[OpenAI] = None

        if self.api_key:
            self._client = OpenAI(api_key=self.api_key, timeout=self.timeout_seconds, max_retries=0)

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def extract_entities(self, raw_text: str) -> Optional[Dict[str, Any]]:
        if not self._client:
            return None

        prompt = (
            "Extract appointment entities from text. Return ONLY strict JSON with keys "
            "date_phrase, time_phrase, department. Use null when missing. Text: "
            f"{raw_text}"
        )

        def _call() -> Dict[str, Any]:
            response = self._client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": "You extract structured appointment entities as JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )

            text = response.output_text
            parsed = _safe_parse_json(text)
            return {
                "date_phrase": parsed.get("date_phrase"),
                "time_phrase": parsed.get("time_phrase"),
                "department": parsed.get("department"),
            }

        try:
            return with_retry(_call, retries=3, backoff_seconds=0.7)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM extraction failed, using fallback. error=%s", exc)
            return None


def _safe_parse_json(text: str) -> Dict[str, Any]:
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```[a-zA-Z]*", "", candidate).strip("` \n")

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", candidate, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))
