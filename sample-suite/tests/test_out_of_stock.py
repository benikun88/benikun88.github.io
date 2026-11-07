def test_out_of_stock_add_to_cart_is_disabled(product_page, out_of_stock_product):
    product_page.open(out_of_stock_product.id)
    product_page.should_show_name(out_of_stock_product.name)
    product_page.should_block_add_to_cart()
