def test_product_page_shows_price_and_a_spec(product_page, api, stocked_product):
    detail = api.product(stocked_product.id)
    assert detail.specs
    product_page.open(stocked_product.id)
    product_page.should_show_name(stocked_product.name)
    product_page.should_show_price(stocked_product.price)
    product_page.should_show_spec(detail.specs[0].spec_name)
