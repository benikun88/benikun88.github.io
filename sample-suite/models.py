from pydantic import BaseModel, ConfigDict, Field


class ProductImage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    by_name: str
    by_url: str
    source_name: str
    source_url: str
    file_name: str
    title: str


class ProductCategory(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    slug: str


class ProductBrand(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str


class Spec(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    product_id: str
    spec_name: str
    spec_value: str
    spec_unit: str | None = None


class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str
    price: float
    is_location_offer: bool
    is_rental: bool
    co2_rating: str
    in_stock: bool
    is_eco_friendly: bool
    product_image: ProductImage
    category: ProductCategory
    brand: ProductBrand
    specs: list[Spec] | None = None


class ProductList(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    current_page: int
    data: list[Product]
    from_: int = Field(alias="from")
    last_page: int
    per_page: int
    to: int
    total: int


class Category(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    slug: str
    parent_id: str | None = None
