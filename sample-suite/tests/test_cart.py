def test_cart_total_is_unit_price_times_quantity(product_page, cart, stocked_product):
    product_page.open(stocked_product.id)
    unit = product_page.read_unit_price()
    product_page.set_quantity(2)
    product_page.add_to_cart(2)
    cart.open_from_header()
    cart.should_charge(stocked_product.name, unit * 2)
