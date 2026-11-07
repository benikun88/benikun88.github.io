"""Headed Chromium for the public sample. The render script runs under xvfb."""

from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture
def page():
    with sync_playwright() as playwright:
        playwright.selectors.set_test_id_attribute("data-test")
        browser = playwright.chromium.launch(
            headless=False,
            args=["--disable-dev-shm-usage"],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="en-US",
        )
        tab = context.new_page()
        tab.set_default_timeout(20_000)
        try:
            yield tab
        finally:
            context.close()
            browser.close()
