from odoo import api, fields, models, _

class ViewGanttProjectTak(models.Model):
    _inherit = 'project.task'

    date_from = fields.Datetime(string='Planned start', index=True, copy=False)
    date_to = fields.Datetime(string='Planned stop', index=True, copy=False)
    color = fields.Integer('Task color', default=4)
    task_progress = fields.Integer(string='Task Progress', default=0)
    
    @api.onchange('date_to')
    def onchange_gantt_stop_date(self):
        if self.date_from and self.date_to and self.date_to < self.date_from:
            self.date_to = self.date_from