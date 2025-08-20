""" import modules """
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoice_request_id = fields.Many2one(
        'invoice.request',
        string="Invoice Request",
        help="Link to the invoice request associated with this sale order."
    )

    @api.model
    def write_with_sudo(self, ids, values):
        """ Override the write method to allow writing with sudo for xmlrpc calls """
        return self.browse(ids).sudo().write(values)

    def action_create_invoice_request(self):
        """ Create an invoice request for the sale order """
        self.ensure_one()
        invoice_request = self.env['invoice.request'].create({
            'name': f"Invoice Request for {self.name}",
            'partner_id': self.partner_id.id,
            'sale_id': self.id,
        })
        self.invoice_request_id = invoice_request.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'invoice.request',
            'res_id': invoice_request.id,
            'view_mode': 'form',
            'target': 'new',
        }
