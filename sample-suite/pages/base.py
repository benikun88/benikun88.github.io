class BasePage:
    def __init__(self, page) -> None:
        self.page = page

    def goto(self, path: str) -> None:
        self.page.goto(path, wait_until="domcontentloaded")
