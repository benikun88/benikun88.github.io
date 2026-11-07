"""Page objects for the public practice shop.

The only target is https://practicesoftwaretesting.com/.
The catalog is synthetic demo data. These objects do not log in.
"""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect

SHOP_URL = "https://practicesoftwaretesting.com/"


class Shop:
    def __init__(self, page: Page) -> None:
        self.page = page

    def open_home(self) -> None:
        self.page.goto(SHOP_URL, wait_until="domcontentloaded")
        self.page.get_by_test_id("product-name").first.wait_for(state="visible")

    def search(self, term: str) -> None:
        field = self.page.get_by_test_id("search-query")
        field.wait_for(state="visible")
        field.fill(term)
        self.page.get_by_test_id("search-submit").click()
        expect(self.page.get_by_test_id("product-name").first).to_contain_text(
            term, ignore_case=True
        )

    def filter_category(self, name: str) -> None:
        label = self.page.locator("label").filter(has_text=name).first
        label.scroll_into_view_if_needed()
        label.wait_for(state="visible")
        label.click()
        self.page.get_by_test_id("product-name").first.wait_for(state="visible")

    def open_first_in_stock_product(self) -> None:
        total = self.page.get_by_test_id("product-name").count()
        for index in range(total):
            self.page.get_by_test_id("product-name").nth(index).click()
            add = self.page.get_by_test_id("add-to-cart")
            add.wait_for(state="visible")
            out_of_stock = self.page.get_by_test_id("out-of-stock").count() > 0
            if add.is_enabled() and not out_of_stock:
                return
            self.page.go_back(wait_until="domcontentloaded")
            self.page.get_by_test_id("product-name").first.wait_for(state="visible")
        raise AssertionError("No in-stock product on the home page")

    def add_to_cart(self) -> None:
        button = self.page.get_by_test_id("add-to-cart")
        button.wait_for(state="visible")
        button.click()
        expect(self.page.get_by_test_id("nav-cart")).to_contain_text(
            re.compile(r"\d")
        )

    def open_cart(self) -> None:
        self.page.get_by_test_id("nav-cart").click()
        self.page.get_by_test_id("cart-total").wait_for(state="visible")

    def cart_total(self) -> str:
        return " ".join(self.page.get_by_test_id("cart-total").inner_text().split())
