""" import modules """
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.portal.controllers.portal import pager as portal_pager

import logging
_logger = logging.getLogger(__name__)

class ExternalSaleInvoiceForm(payment_portal.PaymentPortal):
    def _prepare_invoicerequest_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
        ]

    def _get_request_searchbar_sortings(self):
        return {
            'order': {'label': _('Sale Order'), 'order': 'sale_id desc'},
            'invoice': {'label': _('Invoice'), 'order': 'invoice_id desc'},
            'status': {'label': _('Status'), 'order': 'status'},
        }

    def _prepare_invoicerequest_portal_rendering_values(
        self, page=1, sortby=None, quotation_page=False, **kwargs
    ):
        InvoiceRequest = request.env['invoice.request']

        if not sortby:
            sortby = 'order'

        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()

        if not quotation_page:
            url = "/sale_invoice_xmlrpc/external_sale_invoice_form"
            domain = self._prepare_invoicerequest_domain(partner)

        searchbar_sortings = self._get_request_searchbar_sortings()

        sort_order = searchbar_sortings[sortby]['order']
        print(f"Sort order: {sort_order}")
        pager_values = portal_pager(
            url=url,
            total=InvoiceRequest.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={'sortby': sortby},
        )
        requests = InvoiceRequest.search(domain, order=sort_order, limit=self._items_per_page, offset=pager_values['offset'])

        values.update({
            'requests': requests.sudo() if not quotation_page else InvoiceRequest,
            'page_name': 'request',
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return values

    @http.route(['/sale_invoice_xmlrpc/external_sale_invoice_form', '/sale_invoice_xmlrpc/external_sale_invoice_form/page/<int:page>'], type='http', auth="public", website=True)
    def portal_my_invoice_requests(self, access_token=None, **kwargs):
        """ Render the portal page for invoice requests """
        # Adding case where user is not logged in but has an access token
        if access_token:
            user_id = request.env["res.users.apikeys"]._check_credentials(scope='odoo.plugin.outlook', key=access_token)
            if not user_id:
                raise AccessError(_('Access token invalid'))
            request.update_env(user=user_id)
            request.update_context(**request.env.user.context_get())
        values = self._prepare_invoicerequest_portal_rendering_values(quotation_page=False,**kwargs)
        request.session['my_orders_history'] = values['requests'].ids[:100]
        return request.render("sale_invoice_xmlrpc.portal_my_invoice_requests", values)

    @http.route('/sale_invoice_xmlrpc/external_sale_invoice_form/<int:invoice_request_id>', type='http', auth='public', website=True)
    def external_sale_invoice_form(self, invoice_request_id, report_type='pdf', download=False, access_token=None, **kwargs):
        """ Render the external sale invoice form """
        try:
            requests_sudo = self._document_check_access('invoice.request', invoice_request_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/sale_invoice_xmlrpc/external_sale_invoice_form')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(
                model=requests_sudo.invoice_id,
                report_type=report_type,
                report_ref='account.account_invoices',
                download=download,
            )

        return request.render('sale_invoice_xmlrpc.external_sale_invoice_form', {})
