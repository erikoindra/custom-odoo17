import xmlrpc.client

url = "http://100.66.82.55:8069"
database = "v17_mc_test"
user = "admin"
password = "e1358b3eb958464c2788216c0da14f7a6e8a58a7"
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common".format(url))
uid = common.authenticate(database, user, password, {})

objects = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object".format(url))

partner_ids = objects.execute_kw(
    database, 
    uid, 
    password,
    'res.partner',
    'search_read',
    [[['is_company', '=', True]]],
    {'fields': ['id', 'name', 'email']}
)

to_invoice_sale_ids = objects.execute_kw(
    database, 
    uid, 
    password,
    'sale.order',
    'search_read',
    [[['invoice_status', '=', 'to invoice']]],
    {'fields': ['id', 'name', 'partner_id', 'amount_total']},
)

print(partner_ids)
print(to_invoice_sale_ids)
