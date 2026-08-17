"""Simple Page Object for the demo login page."""


class LoginPage:
    def __init__(self, page, healer):
        self.page = page
        self.healer = healer

        self.username_locator = "#username"
        self.password_locator = "#password"

        # Intentionally wrong on purpose - the real button id is "login-button".
        # This is what the Healer is meant to detect and fix at runtime.
        self.login_button_locator = "#login-btn"

        self.success_locator = "#welcome-message"

    def open(self, url: str) -> None:
        self.page.goto(url)

    def enter_username(self, username: str) -> None:
        self.page.locator(self.username_locator).fill(username)

    def enter_password(self, password: str) -> None:
        self.page.locator(self.password_locator).fill(password)

    def click_login(self):
        """Uses the Healer instead of a raw Playwright click so a broken
        locator can be self-healed instead of immediately failing the test."""
        return self.healer.smart_click(
            self.login_button_locator, description="Login button"
        )

    def is_login_successful(self) -> bool:
        return self.page.locator(self.success_locator).is_visible()
