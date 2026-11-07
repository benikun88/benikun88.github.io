def test_search_finds_named_product(home, stocked_product):
    home.open()
    home.search(stocked_product.name)
    home.should_show_product(stocked_product.name)
