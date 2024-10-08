# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import json
import logging
from datetime import date

import requests
from requests.auth import HTTPBasicAuth
from werkzeug.utils import redirect

from odoo import Command, _, api, fields, models
from odoo.addons.payment import utils as payment_utils
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.osv import expression

_logger = logging.getLogger(__name__)

class PaymentMethod(models.Model):
    _name = 'payment.method'
    _description = "Payment Method"
    _order = 'active desc, sequence, name'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(
        string="Code", help="The technical code of this payment method.", required=True
    )
    sequence = fields.Integer(string="Sequence", default=1)
    primary_payment_method_id = fields.Many2one(
        string="Primary Payment Method",
        help="The primary payment method of the current payment method, if the latter is a brand."
             "\nFor example, \"Card\" is the primary payment method of the card brand \"VISA\".",
        comodel_name='payment.method',
    )
    brand_ids = fields.One2many(
        string="Brands",
        help="The brands of the payment methods that will be displayed on the payment form.",
        comodel_name='payment.method',
        inverse_name='primary_payment_method_id',
    )
    is_primary = fields.Boolean(
        string="Is Primary Payment Method",
        compute='_compute_is_primary',
        search='_search_is_primary',
    )
    provider_ids = fields.Many2many(
        string="Providers",
        help="The list of providers supporting this payment method.",
        comodel_name='payment.provider',
    )
    active = fields.Boolean(string="Active", default=True)
    image = fields.Image(
        string="Image",
        help="The base image used for this payment method; in a 64x64 px format.",
        max_width=64,
        max_height=64,
        required=True,
    )
    image_payment_form = fields.Image(
        string="The resized image displayed on the payment form.",
        related='image',
        store=True,
        max_width=45,
        max_height=30,
    )

    # Feature support fields.
    support_tokenization = fields.Boolean(
        string="Tokenization Supported",
        help="Tokenization is the process of saving the payment details as a token that can later"
             " be reused without having to enter the payment details again.",
    )
    support_express_checkout = fields.Boolean(
        string="Express Checkout Supported",
        help="Express checkout allows customers to pay faster by using a payment method that"
             " provides all required billing and shipping information, thus allowing to skip the"
             " checkout process.",
    )
    support_refund = fields.Selection(
        string="Type of Refund Supported",
        selection=[('full_only', "Full Only"), ('partial', "Partial")],
        help="Refund is a feature allowing to refund customers directly from the payment in Odoo.",
    )
    supported_country_ids = fields.Many2many(
        string="Supported Countries",
        comodel_name='res.country',
        help="The list of countries in which this payment method can be used (if the provider"
             " allows it). In other countries, this payment method is not available to customers."
    )
    supported_currency_ids = fields.Many2many(
        string="Supported Currencies",
        comodel_name='res.currency',
        help="The list of currencies for that are supported by this payment method (if the provider"
             " allows it). When paying with another currency, this payment method is not available "
             "to customers.",
    )

    #=== COMPUTE METHODS ===#

    def _compute_is_primary(self):
        for payment_method in self:
            payment_method.is_primary = not payment_method.primary_payment_method_id

    def _search_is_primary(self, operator, value):
        if operator == '=' and value is True:
            return [('primary_payment_method_id', '=', False)]
        elif operator == '=' and value is False:
            return [('primary_payment_method_id', '!=', False)]
        else:
            raise NotImplementedError(_("Operation not supported."))

    #=== ONCHANGE METHODS ===#

    @api.onchange('active', 'provider_ids', 'support_tokenization')
    def _onchange_warn_before_disabling_tokens(self):
        """ Display a warning about the consequences of archiving the payment method, detaching it
        from a provider, or removing its support for tokenization.

        Let the user know that the related tokens will be archived.

        :return: A client action with the warning message, if any.
        :rtype: dict
        """
        disabling = self._origin.active and not self.active
        detached_providers = self._origin.provider_ids.filtered(
            lambda p: p.id not in self.provider_ids.ids
        )  # Cannot use recordset difference operation because self.provider_ids is a set of NewIds.
        blocking_tokenization = self._origin.support_tokenization and not self.support_tokenization
        if disabling or detached_providers or blocking_tokenization:
            related_tokens = self.env['payment.token'].with_context(active_test=True).search(
                expression.AND([
                    [('payment_method_id', 'in', (self._origin + self._origin.brand_ids).ids)],
                    [('provider_id', 'in', detached_providers.ids)] if detached_providers else [],
                ])
            )  # Fix `active_test` in the context forwarded by the view.
            if related_tokens:
                return {
                    'warning': {
                        'title': _("Warning"),
                        'message': _(
                            "This action will also archive %s tokens that are registered with this "
                            "payment method. Archiving tokens is irreversible.", len(related_tokens)
                        )
                    }
                }

    @api.onchange('provider_ids')
    def _onchange_provider_ids_warn_before_attaching_payment_method(self):
        """ Display a warning before attaching a payment method to a provider.

        :return: A client action with the warning message, if any.
        :rtype: dict
        """
        attached_providers = self.provider_ids.filtered(
            lambda p: p.id.origin not in self._origin.provider_ids.ids
        )
        if attached_providers:
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _(
                        "Please make sure that %(payment_method)s is supported by %(provider)s.",
                        payment_method=self.name,
                        provider=', '.join(attached_providers.mapped('name'))
                    )
                }
            }

    #=== CRUD METHODS ===#

    def write(self, values):
        # Handle payment methods being archived, detached from providers, or blocking tokenization.
        archiving = values.get('active') is False
        detached_provider_ids = [
            vals[0] for command, *vals in values['provider_ids'] if command == Command.UNLINK
        ] if 'provider_ids' in values else []
        blocking_tokenization = values.get('support_tokenization') is False
        if archiving or detached_provider_ids or blocking_tokenization:
            linked_tokens = self.env['payment.token'].with_context(active_test=True).search(
                expression.AND([
                    [('payment_method_id', 'in', (self + self.brand_ids).ids)],
                    [('provider_id', 'in', detached_provider_ids)] if detached_provider_ids else [],
                ])
            )  # Fix `active_test` in the context forwarded by the view.
            linked_tokens.active = False

        # Prevent enabling a payment method if it is not linked to an enabled provider.
        if values.get('active'):
            for pm in self:
                primary_pm = pm if pm.is_primary else pm.primary_payment_method_id
                if (
                    not primary_pm.active  # Don't bother for already enabled payment methods.
                    and all(p.state == 'disabled' for p in primary_pm.provider_ids)
                ):
                    raise UserError(_(
                        "This payment method needs a partner in crime; you should enable a payment"
                        " provider supporting this method first."
                    ))

        return super().write(values)

    # === BUSINESS METHODS === #

    def _get_compatible_payment_methods(
        self, provider_ids, partner_id, currency_id=None, force_tokenization=False,
        is_express_checkout=False, **kwargs
    ):
        """ Search and return the payment methods matching the compatibility criteria.

        The compatibility criteria are that payment methods must: be supported by at least one of
        the providers; support the country of the partner if it exists; be primary payment methods
        (not a brand). If provided, the optional keyword arguments further refine the criteria.

        :param list provider_ids: The list of providers by which the payment methods must be at
                                  least partially supported to be considered compatible, as a list
                                  of `payment.provider` ids.
        :param int partner_id: The partner making the payment, as a `res.partner` id.
        :param int currency_id: The payment currency, if known beforehand, as a `res.currency` id.
        :param bool force_tokenization: Whether only payment methods supporting tokenization can be
                                        matched.
        :param bool is_express_checkout: Whether the payment is made through express checkout.
        :param dict kwargs: Optional data. This parameter is not used here.
        :return: The compatible payment methods.
        :rtype: payment.method
        """
        # Compute the base domain for compatible payment methods.
        domain = [('provider_ids', 'in', provider_ids), ('is_primary', '=', True)]

        # Handle the partner country; allow all countries if the list is empty.
        partner = self.env['res.partner'].browse(partner_id)
        if partner.country_id:  # The partner country must either not be set or be supported.
            domain = expression.AND([
                domain, [
                    '|',
                    ('supported_country_ids', '=', False),
                    ('supported_country_ids', 'in', [partner.country_id.id]),
                ]
            ])

        # Handle the supported currencies; allow all currencies if the list is empty.
        if currency_id:
            domain = expression.AND([
                domain, [
                    '|',
                    ('supported_currency_ids', '=', False),
                    ('supported_currency_ids', 'in', [currency_id]),
                ]
            ])

        # Handle tokenization support requirements.
        if force_tokenization:
            domain = expression.AND([domain, [('support_tokenization', '=', True)]])

        # Handle express checkout.
        if is_express_checkout:
            domain = expression.AND([domain, [('support_express_checkout', '=', True)]])

        # Search the payment methods matching the compatibility criteria.
        compatible_payment_methods = self.env['payment.method'].search(domain)
        return compatible_payment_methods

    def _get_from_code(self, code, mapping=None):
        """ Get the payment method corresponding to the given provider-specific code.

        If a mapping is given, the search uses the generic payment method code that corresponds to
        the given provider-specific code.

        :param str code: The provider-specific code of the payment method to get.
        :param dict mapping: A non-exhaustive mapping of generic payment method codes to
                             provider-specific codes.
        :return: The corresponding payment method, if any.
        :type: payment.method
        """
        generic_to_specific_mapping = mapping or {}
        specific_to_generic_mapping = {v: k for k, v in generic_to_specific_mapping.items()}
        return self.search([('code', '=', specific_to_generic_mapping.get(code, code))], limit=1)

    # Customize
    # <> HDFC APIs
    # Session API
    def _call_session_api(self, payload):
        try:
            headers = {"Content-Type": "application/json", "x-merchantid": payment_utils.MERCHANTID,  "x-customerid": payment_utils.CUSTOMERID}
            response = requests.post(payment_utils.SESSION_URL, json=payload, headers=headers, auth=HTTPBasicAuth(payment_utils.HDFC_API_KEY, ""))
        except Exception as e:
            print(str(e))
            _logger.exception("Unable to reach endpoint at %s", payment_utils.SESSION_URL)
            raise ValidationError("Could not establish the connection to the API.")
        
        return response.json()

    # Order status API
    def _call_order_status_api(self, payload):
        try:
            print('_call_order_status_api')
            headers = {"Content-Type": "application/json", "x-merchantid": payment_utils.MERCHANTID,  "x-customerid": payment_utils.CUSTOMERID}
            response = requests.post(payment_utils.ORDER_STATUS_URL, json=payload, headers=headers, auth=HTTPBasicAuth(payment_utils.HDFC_API_KEY, ""))
        except Exception as e:
            print(str(e))
            _logger.exception("Unable to reach endpoint at %s", payment_utils.ORDER_STATUS_URL)
            raise ValidationError("Could not establish the connection to the API.")
        
        return response.json()
    
    # Get payment receipt
    def get_payment_receipt(self, invoice_id):
        print('>>>>>>get_payment_receipt>>>>>>>>')
        invoice_obj = self.env['account.move']
        payment_obj = self.env['account.payment']

        # Fetch the invoice
        invoice = invoice_obj.browse(invoice_id)
        if not invoice:
            raise ValueError("Invoice not found.")

        # Find associated payments
        print('Move Id = ', invoice.id)
        payments = payment_obj.search([('move_id', 'in', [invoice.id])])

        # Generate report (e.g., PDF) - Assuming the report action is linked in Odoo
        if payments:
            # This method triggers the standard payment receipt PDF generation
            report_action = self.env['ir.actions.report']
            pdf_content = report_action._get_report_from_name(
                'account.report_payment_receipt'
            ).render_qweb_pdf([payment.id for payment in payments])

            return pdf_content[0]  # The PDF binary content
        else:
            raise ValueError("No payments found for this invoice.")   
        # </>

    # Send invoice after payment
    def send_invoice_to_customer(self, invoice):
        # self.env.ref('account.account_invoices').sudo()._render_qweb_pdf([invoice_id])
        pdf_content, _ = self.env['ir.actions.report'].sudo()._render_qweb_pdf("account.account_invoices", invoice.id)
        # pdf_content, _ = self.env.ref('account.account_invoices')._render_qweb_pdf([invoice.id])
        pdf_base64 = base64.b64encode(pdf_content)
        
        attachment = self.env['ir.attachment'].sudo().create({
            'name': 'Invoice.pdf',
            'type': 'binary',
            'datas': pdf_base64,
            'res_model': 'account.move',
            'res_id': invoice.id,
            'mimetype': 'application/pdf',
            # 'res_model': 'account.move',
        })
        
        print('Email = ', invoice.partner_id.email)
        email_values = {
                'subject': f'Invoice {invoice.name}',
                'body_html': f'<p>Hello,</p><p>Please find attached your invoice {invoice.name}.</p>',
                'email_to': invoice.partner_id.email,
                'email_from': 'erp@cigi.org',
                'email_cc': False,
                'auto_delete': True,
                'attachment_ids': [(4, attachment.id)] 
            }
        
        mail = self.env['mail.mail'].sudo().create(email_values)
        mail.send()
        

    # Create invoice after successfull payment
    def _create_invoice_after_payment(self, order, order_line):
         # Get selected users currency

        invoice_lines = []
        for line in order_line:
            vals = {
                'name': line.name,
                'price_unit': line.price_unit,
                'quantity': line.product_uom_qty,
                'product_id': line.product_id.id,
                'product_uom_id': line.product_uom.id,
                'tax_ids': [(6, 0, line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [line.id])],
            }
            invoice_lines.append((0, 0, vals))
        
        print('Currency Id = ', order.currency_id.id)
        invoice_obj = self.env['account.move'].create({
            'ref': order.client_order_ref,
            'move_type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'partner_id': order.partner_invoice_id.id,
            'currency_id': order.currency_id.id,
            'invoice_line_ids': invoice_lines
        })

        invoice_obj.sudo().action_post()
        print("Invoice Created")
        
        # <> Register invoice payment
        journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
        payment_register_vals = {
            'partner_id': invoice_obj.partner_id.id,
            'amount': invoice_obj.amount_total,
            'journal_id': invoice_obj.journal_id.id,  # The journal where the payment is registered (e.g., bank)
            'payment_method_line_id': journal.inbound_payment_method_line_ids[0].id, # payment_id.id,  # The payment method (manual, bank)
            'company_id': invoice_obj.company_id.id,  # Link payment to the invoice
        }
        payment_register = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=[invoice_obj.id]).sudo().create(payment_register_vals)
        payment_register.action_create_payments()
        print("Payment Registered")
        # </>

        self.send_invoice_to_customer(invoice_obj) # Sending invoice to customer
        print("Mail Sent")
        # </>

    # Redirect to HDFC payment page
    def _redirect_to_payment_page(self, order_id, name, amount, email, phone, desc, callback_url):
        payload = {
                'order_id': order_id,
                'amount': amount,
                'customer_id': order_id,
                'customer_email': email,
                'customer_phone': phone,
                'payment_page_client_id': 'hdfcmaster',
                'action': "paymentPage",
                'currency': "INR",
                'return_url': callback_url,
                'description': desc,
                'first_name': name,
                'last_name': ''
            }
        jsonres = self._call_session_api(payload)
        payment_link = jsonres['payment_links']['web']

        print('Payment Link = '+payment_link)
        return payment_link