"""
Talks to an OpenAI-compatible chat completions endpoint to get replacement
locator suggestions for an element that could not be found.

Important: this class NEVER executes anything the model returns. It only
ever returns plain data (a list of dicts). Whether a suggested locator is
actually used is decided later by LocatorValidator + Healer.
"""

import json
from typing import Dict, List

import requests

from utils.config import LLM_API_BASE, LLM_API_KEY, LLM_MODEL, LLM_REQUEST_TIMEOUT

SYSTEM_PROMPT = """You are a QA automation assistant. Your ONLY job is to suggest replacement \
Playwright locators for a web element that could not be found. \
You must NEVER write, suggest, or execute any Python code, JavaScript, or shell commands. \
You only return locator strings that are directly usable inside a Playwright \
`page.locator(...)` call (CSS selectors, an `xpath=...` expression, or a `text=...` \
expression are all acceptable).

Prefer locators in this priority order:
1. A data-testid attribute
2. Role + accessible name
3. A label
4. A stable id
5. A stable CSS selector
6. Visible text
7. XPath (only as a last resort)

Avoid fragile selectors such as `div:nth-child(3)` or long CSS paths based on DOM position.

Respond with STRICTLY valid JSON and nothing else. No markdown, no code fences, no \
explanations outside the JSON. Use exactly this shape:

{
  "suggestions": [
    {
      "locator": "#login-button",
      "type": "css",
      "confidence": 0.95,
      "reason": "The button id matches the login button in the DOM."
    }
  ]
}
"""


class AILocatorEngine:
    """Builds the prompt, calls the LLM, and safely parses its JSON response."""

    def __init__(self):
        self.api_key = LLM_API_KEY
        self.api_base = LLM_API_BASE
        self.model = LLM_MODEL

    def _build_user_prompt(
        self, failed_locator: str, error_message: str, dom_snippet: str, description: str
    ) -> str:
        return f"""A Playwright action failed.

Action description: {description or 'N/A'}
Failed locator: {failed_locator}
Error message: {error_message}

Relevant DOM snippet (may be truncated):
---
{dom_snippet}
---

Suggest up to 3 replacement locators that would work with this DOM, following the \
priority order and JSON format described in your instructions."""

    def suggest_locators(
        self,
        failed_locator: str,
        error_message: str,
        dom_snippet: str,
        description: str = "",
        max_suggestions: int = 3,
    ) -> List[Dict]:
        """Returns a list of suggestion dicts, sorted by confidence (highest first).
        Returns an empty list if the API key is missing, the request fails, or the
        response cannot be parsed - callers must handle that gracefully."""

        if not self.api_key:
            print("[AILocatorEngine] LLM_API_KEY is not set - skipping AI healing.")
            return []

        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": self._build_user_prompt(
                        failed_locator, error_message, dom_snippet, description
                    ),
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=LLM_REQUEST_TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[AILocatorEngine] Request to LLM API failed: {e}")
            return []

        try:
            content = response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as e:
            print(f"[AILocatorEngine] Unexpected LLM API response shape: {e}")
            return []

        suggestions = self._parse_suggestions(content)
        suggestions.sort(key=lambda s: s.get("confidence", 0) or 0, reverse=True)
        return suggestions[:max_suggestions]

    @staticmethod
    def _parse_suggestions(content: str) -> List[Dict]:
        """Safely parses the model's JSON response. Handles the common case of
        the model wrapping JSON in ```json ... ``` fences despite instructions."""
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"[AILocatorEngine] Could not parse LLM response as JSON: {e}")
            return []

        suggestions = data.get("suggestions", [])
        if not isinstance(suggestions, list):
            print("[AILocatorEngine] 'suggestions' was not a list - ignoring response.")
            return []

        valid_suggestions = [
            s for s in suggestions if isinstance(s, dict) and s.get("locator")
        ]
        return valid_suggestions
