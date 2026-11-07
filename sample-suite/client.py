import json
import urllib.error
import urllib.parse
import urllib.request

from models import Category, Product, ProductList


class ApiError(Exception):
    pass


class PracticeApi:
    def __init__(self, base: str = "https://api.practicesoftwaretesting.com") -> None:
        self.base = base

    def get_json(self, path: str, params: dict | None = None):
        query = ""
        if params:
            kept = {key: value for key, value in params.items() if value is not None}
            query = "?" + urllib.parse.urlencode(kept)
        url = f"{self.base}{path}{query}"
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "beni-portfolio-sample/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as exc:
            raise ApiError(f"{exc.code} {url}") from exc

    def product_list(self, page: int = 1, **params) -> ProductList:
        payload = self.get_json("/products", {"page": page, **params})
        return ProductList.model_validate(payload)

    def iter_products(self, **params):
        page_no = 1
        while True:
            listing = self.product_list(page=page_no, **params)
            yield from listing.data
            if page_no >= listing.last_page or not listing.data:
                break
            page_no += 1

    def product(self, product_id: str) -> Product:
        return Product.model_validate(self.get_json(f"/products/{product_id}"))

    def categories(self) -> list[Category]:
        payload = self.get_json("/categories")
        return [Category.model_validate(item) for item in payload]
