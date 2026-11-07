def test_product_detail_matches_list_item(api):
    listing = api.product_list()
    matched = None
    for item in listing.data:
        detail = api.product(item.id)
        assert detail.id == item.id
        assert detail.name == item.name
        assert detail.price == item.price
        if detail.specs:
            matched = detail
            break
    assert matched is not None
    assert matched.specs[0].spec_name
    assert matched.specs[0].product_id == matched.id
