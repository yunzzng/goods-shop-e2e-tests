from playwright.sync_api import expect

from pages.login_page import LoginPage

BASE_URL = "https://lovely-goods-shop.vercel.app"
VALID_EMAIL = "demo@lovelygoods.test"
VALID_PASSWORD = "demo1234"


def test_login(page, login_success_close_delay_ms):
    login_page = LoginPage(page)
    login_page.go_to(BASE_URL)
    login_page.login(VALID_EMAIL, VALID_PASSWORD)
    login_page.wait_for_login_success()
    page.wait_for_timeout(login_success_close_delay_ms)


def test_login_page_shows_default_test_account(page):
    login_page = LoginPage(page)
    login_page.go_to(BASE_URL)

    expect(page.get_by_text("기본 테스트 계정")).to_be_visible()
    expect(page.get_by_text(VALID_EMAIL)).to_be_visible()


def test_login_fails_with_empty_email(page):
    login_page = LoginPage(page)
    login_page.go_to(BASE_URL)

    login_page.login("", VALID_PASSWORD)

    expect(page.get_by_text("이메일을 입력해주세요.")).to_be_visible()
    expect(page).to_have_url(f"{BASE_URL}/login")


def test_login_fails_with_wrong_password(page):
    login_page = LoginPage(page)
    login_page.go_to(BASE_URL)

    login_page.login(VALID_EMAIL, "wrong-password")

    expect(page.get_by_text("이메일 또는 비밀번호를 확인해주세요.")).to_be_visible()
    expect(page).to_have_url(f"{BASE_URL}/login")
