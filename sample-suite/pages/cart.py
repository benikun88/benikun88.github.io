import re
from decimal import Decimal

from playwright.sync_api import expect

from pages.base import BasePage


class CartPage(BasePage):
    def open_from_header(self) -> None:
        self.page.get_by_role("link", name="cart").click()
        expect(self.page).to_have_url(re.compile(r".*/checkout$"))

    def should_charge(self, product_name: str, total: Decimal) -> None:
        expect(self.page.get_by_text(product_name).first).to_be_visible()
        amount = f"${total.quantize(Decimal('0.01'))}"
        expect(self.page.get_by_text(amount, exact=True)).to_have_count(2)
