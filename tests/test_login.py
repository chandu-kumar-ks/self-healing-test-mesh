"""
Demo test for the Self-Healing Test Mesh.

The login button locator used by LoginPage ("#login-btn") is intentionally
wrong - the real id in demo/login.html is "login-button". This test proves
that the framework detects the failure, asks the AI for a fix, validates
it, retries the click, and still ends up PASSED.
"""

from pathlib import Path

from pages.login_page import LoginPage

DEMO_PAGE = Path(__file__).parent.parent / "demo" / "login.html"


def test_login_with_self_healing(page, healer):
    login_page = LoginPage(page, healer)

    login_page.open(f"file://{DEMO_PAGE.resolve()}")
    login_page.enter_username("admin")
    login_page.enter_password("admin123")
    login_page.click_login()

    assert login_page.is_login_successful(), (
        "Login was not successful even after self-healing was attempted"
    )
