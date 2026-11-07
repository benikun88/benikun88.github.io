import re

from playwright.sync_api import expect

from pages.base import BasePage


class AccountPage(BasePage):
    def should_be_open(self) -> None:
        expect(self.page).to_have_url(re.compile(r".*/account$"))
        expect(self.page.get_by_role("heading", name="My account")).to_be_visible()
        expect(self.page.get_by_role("link", name="Invoices", exact=True)).to_be_visible()
        expect(self.page.get_by_role("link", name="Sign in")).to_have_count(0)

    def open_invoices(self) -> None:
        self.page.get_by_role("link", name="Invoices", exact=True).click()
        expect(self.page).to_have_url(re.compile(r".*/account/invoices$"))
        expect(self.page.get_by_role("heading", name="Invoices")).to_be_visible()

    def should_list_invoice_numbers(self) -> None:
        expect(self.page.get_by_role("columnheader", name="Invoice Number")).to_be_visible()
        expect(self.page.get_by_role("cell", name=re.compile(r"INV-\d+")).first).to_be_visible()
