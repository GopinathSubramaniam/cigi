from odoo import fields, models,api


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    
    allocation_journal = fields.Many2one(
        'account.journal', string="Allocation Journal",
        domain=[('type', '=', 'general')], 
    )
    