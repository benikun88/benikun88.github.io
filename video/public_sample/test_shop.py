"""Public shop checks used by the showreel.

Search, filter, and add to cart. Serial. No login.
"""

from __future__ import annotations

import re

from playwright.sync_api import expect

from pages import Shop


def test_search_lists_products(page):
    shop = Shop(page)
    shop.open_home()
    shop.search("hammer")
    expect(page.get_by_test_id("product-name").first).to_be_visible()
    assert "hammer" in page.get_by_test_id("product-name").first.inner_text().lower()


def test_filter_then_add_to_cart(page):
    shop = Shop(page)
    shop.open_home()
    shop.filter_category("Hand Tools")
    shop.open_first_in_stock_product()
    shop.add_to_cart()
    shop.open_cart()
    total = shop.cart_total()
    assert re.search(r"\d", total)
