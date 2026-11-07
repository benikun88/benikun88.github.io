def test_sign_in_opens_the_account_page(login, account, customer):
    login.open()
    login.sign_in(customer.EMAIL, customer.PASSWORD)
    account.should_be_open()
