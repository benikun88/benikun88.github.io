def test_product_list_matches_schema(api):
    listing = api.product_list()
    assert listing.current_page == 1
    assert listing.total >= len(listing.data) >= 1
    for product in listing.data:
        assert product.price > 0
        assert product.name
        assert product.category.slug
        assert product.brand.name
        assert product.product_image.file_name
