from odoo import api, fields, models, _

class IrUiView(models.Model):
    _inherit = 'ir.ui.view'
    
    type = fields.Selection(selection_add=[
        ('ganttview', "Gantt View")
        ], ondelete={'ganttview': 'cascade'})