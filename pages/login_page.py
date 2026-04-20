import re

from playwright.sync_api import expect


class LoginPage:
    def __init__(self, page):
        self.page = page
        self.email_input = 'input[name="email"]'
        self.password_input = 'input[name="password"]'
        self.login_button = 'button[type="submit"]'

    def go_to(self, base_url: str):
        self.page.goto(f"{base_url}/login", wait_until="domcontentloaded")
        expect(self.page.locator(self.email_input)).to_be_visible()
        expect(self.page.locator(self.password_input)).to_be_visible()

    def login(self, email: str, password: str):
        self.page.fill(self.email_input, email)
        self.page.fill(self.password_input, password)
        self.page.click(self.login_button)

    def wait_for_login_success(self):
        self.page.wait_for_load_state("networkidle")
        expect(self.page).not_to_have_url(re.compile(r".*/login/?$"))
