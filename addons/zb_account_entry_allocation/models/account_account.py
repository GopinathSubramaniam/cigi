from odoo import models, fields

class AccountAccount(models.Model):
    _inherit = 'account.account'

    allocate_entries = fields.Boolean(string='Allocate Entries')
