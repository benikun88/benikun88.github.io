from pathlib import Path

import pytest
from faker import Faker
from playwright.sync_api import expect

import practice_account
from client import PracticeApi
from pages.account import AccountPage
from pages.cart import CartPage
from pages.home import HomePage
from pages.login import LoginPage
from pages.product import ProductPage

expect.set_options(timeout=15_000)
Path(__file__).resolve().parent.joinpath("reports").mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "headless": False,
        "args": ["--disable-blink-features=AutomationControlled"],
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1440, "height": 1000},
    }


@pytest.fixture
def shop_page(page):
    page.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    page.set_default_timeout(20_000)
    page.set_default_navigation_timeout(45_000)
    return page


@pytest.fixture(scope="session")
def api():
    return PracticeApi()


@pytest.fixture(scope="session")
def catalog(api):
    return list(api.iter_products())


@pytest.fixture(scope="session")
def stocked_product(api, catalog):
    fake = Faker()
    fake.seed_instance(7)
    safe = [
        product
        for product in catalog
        if product.in_stock
        and not product.is_rental
        and product.price > 0
        and "Thor" not in product.name
    ]
    if not safe:
        pytest.skip("The shop has no stocked product to buy")
    start = fake.random_element(elements=safe)
    ordered = [start] + [product for product in safe if product.id != start.id]
    for product in ordered[:8]:
        detail = api.product(product.id)
        if detail.specs:
            return product
    pytest.skip("No stocked product with a published specification")


@pytest.fixture(scope="session")
def out_of_stock_product(catalog):
    for product in catalog:
        if not product.in_stock and not product.is_rental:
            return product
    pytest.skip("The shop has no out-of-stock product")


@pytest.fixture
def faker():
    fake = Faker()
    fake.seed_instance(7)
    return fake


@pytest.fixture
def home(shop_page):
    return HomePage(shop_page)


@pytest.fixture
def product_page(shop_page):
    return ProductPage(shop_page)


@pytest.fixture
def cart(shop_page):
    return CartPage(shop_page)


@pytest.fixture
def login(shop_page):
    return LoginPage(shop_page)


@pytest.fixture
def account(shop_page):
    return AccountPage(shop_page)


@pytest.fixture
def customer():
    return practice_account
