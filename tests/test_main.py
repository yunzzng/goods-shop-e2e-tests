def test_main_page_open(page):
    page.goto("https://lovely-goods-shop.vercel.app/")
    assert page.title() is not None