import xmlrpc.client
import getpass

url = "http://localhost:8069"
database = "v17_mc"
user = str(input("Enter your Odoo username: "))
password = getpass.getpass("Enter your Odoo token: ")

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common".format(url))
uid = common.authenticate(database, user, password, {})

objects = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object".format(url))

to_invoice_sale_ids = objects.execute_kw(
    database, 
    uid, 
    password,
    'sale.order',
    'search_read',
    [[['invoice_status', '=', 'to invoice'], ['invoice_request_id', '=', False]]],
    {'fields': ['id', 'name', 'partner_id', 'amount_total']},
)

print("To invoice sales: ", to_invoice_sale_ids)

invoice_request = str(input("Do you want to create invoices for these sales? (yes/no): ")).strip().lower()

if invoice_request == 'no':
    print("No invoices will be created.")
elif invoice_request == 'yes':
    which_sales = str(input("Enter the IDs of the sales orders to invoice, separated by commas: ")).strip()
    sales_ids = [int(sale_id.strip()) for sale_id in which_sales.split(',')]
    print("Selected sales IDs: ", sales_ids)
    partner_id = list(set(sale['partner_id'][0] for sale in to_invoice_sale_ids if sale['id'] in sales_ids))
    print("Partner ID for selected sales orders: ", partner_id)

    # Create invoice requests for each sales order and collect their IDs
    request_ids = []
    for sale_id in sales_ids:
        request_id = objects.execute_kw(
            database, 
            uid, 
            password,
            'invoice.request',
            'create',
            [{'sale_id': sale_id, 'partner_id': partner_id[0]}]
        )
        request_ids.append(request_id)
    # Update each sale.order with its corresponding invoice_request_id
    for sale_id, request_id in zip(sales_ids, request_ids):
        objects.execute_kw(
            database, 
            uid,        
            password,
            'sale.order',
            'write_with_sudo',
            [[sale_id], {'invoice_request_id': request_id}]
        )
    print("Invoice requests created for sales orders: ID no.", request_ids)
    print("Please kindly access http://localhost:8069/sale_invoice_xmlrpc/external_sale_invoice_form?access_token=your_access_token to view the requests.")
else:
    print("Invalid input. Please enter 'yes' or 'no'.")
print("Process completed.")
