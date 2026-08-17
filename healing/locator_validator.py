"""
Validates a locator suggested by the AI against the live page.

Nothing the AI returns is ever trusted or used blindly - it is always run
through this validator first. This module never executes code, it only
checks whether a locator string resolves to exactly one visible element.
"""

from typing import Tuple


class LocatorValidator:
    """Simple, stateless validator for Playwright locator strings."""

    @staticmethod
    def validate(page, locator: str) -> Tuple[bool, str]:
        """
        Returns (is_valid, reason).

        A locator is considered valid if:
          1. It is a non-empty string.
          2. Playwright can parse it without raising an error.
          3. It matches exactly one element on the page (unique).
          4. That element is visible / usable.
        """
        if not locator or not isinstance(locator, str):
            return False, "Locator is empty or not a string"

        try:
            candidate = page.locator(locator)
            count = candidate.count()
        except Exception as e:
            return False, f"Locator syntax is invalid: {e}"

        if count == 0:
            return False, "No element matches this locator"
        if count > 1:
            return False, f"Locator matches {count} elements, must be unique"

        try:
            is_visible = candidate.is_visible()
        except Exception as e:
            return False, f"Could not determine visibility: {e}"

        if not is_visible:
            return False, "Element is not visible"

        return True, "Locator is valid and usable"
