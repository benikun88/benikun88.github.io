def test_invoices_list_invoice_numbers(login, account, customer):
    login.open()
    login.sign_in(customer.EMAIL, customer.PASSWORD)
    account.open_invoices()
    account.should_list_invoice_numbers()
