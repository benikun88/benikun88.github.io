def test_category_filter_limits_the_grid(home, api, faker):
    name = faker.random_element(elements=("Hammer", "Pliers", "Wrench", "Screwdriver"))
    category = next(item for item in api.categories() if item.name == name)
    allowed = {product.name for product in api.iter_products(by_category=category.id)}
    assert allowed, name
    home.open()
    home.select_category(name)
    home.should_show_only(allowed)
