from playwright.sync_api import expect

from pages.base import BasePage


class LoginPage(BasePage):
    def open(self) -> None:
        self.goto("/auth/login")
        expect(self.page.get_by_role("textbox", name="Email address")).to_be_visible()

    def sign_in(self, email: str, password: str) -> None:
        self.page.get_by_role("textbox", name="Email address").fill(email)
        self.page.get_by_role("textbox", name="Password").fill(password)
        self.page.get_by_role("button", name="Login").click()
