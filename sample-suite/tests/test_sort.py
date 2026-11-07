def test_sort_price_low_to_high(home):
    home.open()
    home.sort_by_price_low_to_high()
    home.should_show_prices_ascending()
