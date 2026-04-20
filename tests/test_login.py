from pages.login_page import LoginPage


def test_login(page, login_success_close_delay_ms):
    login_page = LoginPage(page)
    login_page.go_to("https://lovely-goods-shop.vercel.app")
    login_page.login("demo@lovelygoods.test", "demo134")
    login_page.wait_for_login_success()
    page.wait_for_timeout(login_success_close_delay_ms)
