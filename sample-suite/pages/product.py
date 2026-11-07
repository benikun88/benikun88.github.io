import re
from decimal import Decimal

from playwright.sync_api import expect

from pages.base import BasePage


class ProductPage(BasePage):
    def open(self, product_id: str) -> None:
        self.goto(f"/product/{product_id}")
        expect(self.page.get_by_role("heading", level=1)).to_be_visible()

    def should_show_name(self, name: str) -> None:
        expect(self.page.get_by_role("heading", name=name, level=1)).to_be_visible()

    def should_show_price(self, price: float) -> None:
        expected = Decimal(f"{price:.2f}")
        expect(self.page.get_by_text(f"${expected}", exact=True).first).to_be_visible()

    def should_show_spec(self, spec_name: str) -> None:
        expect(self.page.get_by_text(spec_name, exact=True).first).to_be_visible()

    def read_unit_price(self) -> Decimal:
        text = self.page.get_by_text(re.compile(r"^\$\d+\.\d{2}$")).first.inner_text()
        return Decimal(text.strip().replace("$", ""))

    def set_quantity(self, value: int) -> None:
        spin = self.page.get_by_role("spinbutton", name="Quantity")
        for _ in range(value - 1):
            self.page.get_by_role("button", name="Increase quantity").click()
        expect(spin).to_have_value(str(value))

    def add_to_cart(self, quantity: int) -> None:
        self.page.get_by_role("button", name="Add to cart").click()
        expect(self.page.get_by_role("link", name="cart")).to_contain_text(str(quantity))

    def should_block_add_to_cart(self) -> None:
        expect(self.page.get_by_role("button", name="Add to cart")).to_be_disabled()
        expect(self.page.get_by_text("Out of stock").first).to_be_visible()
