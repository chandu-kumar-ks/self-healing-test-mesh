"""
Orchestrates the self-healing flow for a single Playwright action:

    1. Try the original locator.
    2. On failure, capture the DOM + error and ask the AI for replacements.
    3. Validate each suggestion with Playwright before it is ever used.
    4. Retry the action with the first valid, working suggestion.
    5. Record everything so it can be shown in the HTML report.

The AI is only ever asked for a locator string - it never generates or
runs code, and nothing it returns is used without passing LocatorValidator
first.
"""

from typing import Dict, List

from healing.ai_locator import AILocatorEngine
from healing.locator_validator import LocatorValidator
from utils.config import MAX_HEALING_ATTEMPTS


class Healer:
    def __init__(self, page):
        self.page = page
        self.ai_engine = AILocatorEngine()
        self.validator = LocatorValidator()
        self.max_attempts = MAX_HEALING_ATTEMPTS
        self.healing_log: List[Dict] = []

    def smart_click(self, locator: str, description: str = "") -> Dict:
        """Clicks `locator`. If it fails, attempts self-healing before giving up.
        Raises AssertionError if the action still cannot be completed after
        healing - the original failure is never silently swallowed."""

        event = self._new_event(locator, description)

        try:
            self.page.locator(locator).click(timeout=3000)
            event["original_status"] = "PASSED"
            event["final_status"] = "PASSED"
            self.healing_log.append(event)
            return event
        except Exception as e:
            event["original_status"] = "FAILED"
            event["error"] = str(e)

        event = self._attempt_healing(locator, event, description)
        self.healing_log.append(event)

        if event["final_status"] != "PASSED (HEALED)":
            raise AssertionError(
                f"Self-healing could not fix locator '{locator}'. "
                f"Original error: {event['error']}"
            )
        return event

    def _attempt_healing(self, locator: str, event: Dict, description: str) -> Dict:
        event["healing_attempted"] = True
        dom_snippet = self._capture_dom_snippet()

        suggestions = self.ai_engine.suggest_locators(
            failed_locator=locator,
            error_message=event["error"] or "",
            dom_snippet=dom_snippet,
            description=description,
            max_suggestions=self.max_attempts,
        )

        attempts = 0
        for suggestion in suggestions:
            # Hard safety cap - never try more than max_attempts replacements.
            if attempts >= self.max_attempts:
                break
            attempts += 1

            candidate = suggestion.get("locator")
            if not candidate:
                continue

            is_valid, _reason = self.validator.validate(self.page, candidate)
            if not is_valid:
                continue

            try:
                self.page.locator(candidate).click(timeout=3000)
            except Exception:
                # This suggestion validated but still failed to click - try the next one.
                continue

            event["healed_locator"] = candidate
            event["confidence"] = suggestion.get("confidence")
            event["healing_result"] = "SUCCESS"
            event["final_status"] = "PASSED (HEALED)"
            return event

        event["healing_result"] = "FAILED"
        event["final_status"] = "FAILED"
        return event

    def _capture_dom_snippet(self, max_chars: int = 3000) -> str:
        """Grabs the page HTML, capped to avoid sending an unnecessarily large
        payload to the LLM."""
        try:
            html = self.page.content()
            return html[:max_chars]
        except Exception:
            return ""

    @staticmethod
    def _new_event(locator: str, description: str) -> Dict:
        return {
            "description": description,
            "original_locator": locator,
            "original_status": "UNKNOWN",
            "healing_attempted": False,
            "healed_locator": None,
            "confidence": None,
            "healing_result": None,
            "final_status": None,
            "error": None,
        }
