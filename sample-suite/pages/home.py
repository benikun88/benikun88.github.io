import re
from decimal import Decimal

from playwright.sync_api import expect

from pages.base import BasePage


class HomePage(BasePage):
    def open(self) -> None:
        self.goto("/")
        expect(self.page.get_by_role("textbox", name="Search")).to_be_visible()
        expect(self._product_links().first).to_be_visible()

    def search(self, query: str) -> None:
        field = self.page.get_by_role("textbox", name="Search")
        field.fill(query)
        self.page.get_by_role("button", name="Search", exact=True).click()

    def should_show_product(self, name: str) -> None:
        expect(self.page.get_by_role("link", name=name).first).to_be_visible()

    def select_category(self, name: str) -> None:
        checkbox = self.page.get_by_role("checkbox", name=name, exact=True)
        checkbox.check()
        expect(checkbox).to_be_checked()

    def should_show_only(self, allowed: set[str]) -> None:
        self.page.wait_for_function(
            """(allowed) => {
              const links = [...document.querySelectorAll("a[href*='/product/']")];
              const shown = links
                .map((link) => (link.innerText.split("\\n")[0] || "").trim())
                .filter(Boolean);
              return shown.length > 0 && shown.every((name) => allowed.includes(name));
            }""",
            arg=sorted(allowed),
            timeout=15_000,
        )

    def sort_by_price_low_to_high(self) -> None:
        self.page.get_by_role("combobox", name="sort").select_option(
            label="Price (Low - High)"
        )

    def should_show_prices_ascending(self) -> None:
        self.page.wait_for_function(
            """() => {
              const links = [...document.querySelectorAll("a[href*='/product/']")];
              const prices = links.map((link) => {
                const match = link.innerText.match(/\\$(\\d+\\.\\d{2})/);
                return match ? Number(match[1]) : null;
              }).filter((price) => price !== null);
              if (prices.length < 2) return false;
              for (let index = 1; index < prices.length; index += 1) {
                if (prices[index] < prices[index - 1]) return false;
              }
              return true;
            }""",
            timeout=15_000,
        )

    def product_names(self) -> list[str]:
        names = []
        links = self._product_links()
        for index in range(links.count()):
            line = links.nth(index).inner_text().splitlines()[0].strip()
            if line:
                names.append(line)
        return names

    def product_prices(self) -> list[Decimal]:
        prices = []
        links = self._product_links()
        for index in range(links.count()):
            match = re.search(r"\$(\d+\.\d{2})", links.nth(index).inner_text())
            if match:
                prices.append(Decimal(match.group(1)))
        return prices

    def _product_links(self):
        return self.page.locator("a[href*='/product/']")
