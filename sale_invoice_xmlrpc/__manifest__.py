{
    'name': 'Sale Invoice XMLRPC API',
    'version': '17.0.0.0.1',
    'summary': 'Sale Invoice XMLRPC API',
    'description': """
        Sale Invoice XMLRPC API for Odoo 17.0
    """,
    'sequence': 1,
    'license': 'LGPL-3',
    'category': 'Tool',
    'author': 'Eriko',
    'depends': [
        'sale_management',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/invoice_request_views.xml',
        'views/portal_templates.xml',
    ],
    'installable': True,
    'application': False,
}
