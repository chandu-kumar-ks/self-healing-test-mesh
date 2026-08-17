"""
Shared pytest fixtures:
  - `browser` / `page`: standard Playwright sync setup.
  - `healer`: a fresh Healer per test, whose events are collected here and
    turned into an HTML report once the whole session finishes.
"""

import json
import sys
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

# Make sure "healing", "pages", "utils" are importable regardless of
# where pytest is invoked from.
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from healing.healer import Healer  # noqa: E402
from utils.config import HEADLESS  # noqa: E402
from utils.report_generator import generate_html_report  # noqa: E402

REPORTS_DIR = ROOT_DIR / "reports"
SCREENSHOTS_DIR = ROOT_DIR / "screenshots"
REPORTS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Collects healing events from every test in the session.
_all_healing_events = []


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=HEADLESS)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def healer(page, request):
    h = Healer(page)
    yield h

    _all_healing_events.extend(h.healing_log)

    # Best-effort screenshot for anything that ended up FAILED.
    for event in h.healing_log:
        if event["final_status"] == "FAILED":
            screenshot_path = SCREENSHOTS_DIR / f"{request.node.name}_failed.png"
            try:
                page.screenshot(path=str(screenshot_path))
            except Exception:
                pass


def pytest_sessionfinish(session, exitstatus):
    generate_html_report(_all_healing_events, REPORTS_DIR / "healing_report.html")
    with open(REPORTS_DIR / "healing_report.json", "w", encoding="utf-8") as f:
        json.dump(_all_healing_events, f, indent=2)
