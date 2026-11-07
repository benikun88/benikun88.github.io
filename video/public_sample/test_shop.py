"""Serial sample against the public practice shop.

Produces JUnit for the demo report. This run is serial.
Parallel workers, account locks, and TOTP belong to the framework
and are not executed here.
"""

from __future__ import annotations

import re

from playwright.sync_api import expect

from pages import Shop


def test_home_lists_products(page):
    shop = Shop(page)
    shop.open_home()
    expect(page.get_by_test_id("product-name").first).to_be_visible()


def test_product_shows_price(page):
    shop = Shop(page)
    shop.open_home()
    shop.open_first_in_stock_product()
    price = page.get_by_test_id("unit-price")
    expect(price).to_be_visible()
    assert re.search(r"\d", price.inner_text())


def test_cart_total_after_add(page):
    shop = Shop(page)
    shop.open_home()
    shop.open_first_in_stock_product()
    shop.add_to_cart()
    shop.open_cart()
    total = shop.cart_total()
    assert "$" in total
