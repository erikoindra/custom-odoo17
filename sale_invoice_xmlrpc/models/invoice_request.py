""" import modules """
from odoo import fields, models, _
from odoo.exceptions import UserError

class InvoiceRequest(models.Model):
    _name = "invoice.request"
    _inherit = ['portal.mixin', 'product.catalog.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Invoice Request"

    name = fields.Char(string="Request Name")
    partner_id = fields.Many2one('res.partner', string="Partner", required=True)
    sale_id = fields.Many2one('sale.order', string="Sale Order", required=True)
    invoice_id = fields.Many2one('account.move', string="Invoice")
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ], string="Status", default='pending')

    def action_approve(self):
        """ Approve the invoice request and create an invoice """
        for request in self:
            if request.sale_id:
                invoice = request.sale_id._create_invoices(final=True, grouped=not True)
                request.name = request.sale_id.name
                request.sale_id.invoice_request_id = request.id
                request.invoice_id = invoice.id
                request.status = 'approved'
            else:
                raise UserError(_("No sale order associated with this request."))

    def _get_report_base_filename(self):
        return 'Invoice Request'

    def _compute_access_url(self):
        """ override to set the access URL for the invoice request """
        super()._compute_access_url()
        for order in self:
            order.access_url = f'/sale_invoice_xmlrpc/external_sale_invoice_form/{order.id}'
