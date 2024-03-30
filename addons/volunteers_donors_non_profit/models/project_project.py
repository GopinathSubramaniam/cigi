# -*- coding: utf-8 -*-

from odoo import models, fields

class Project(models.Model):
    _inherit = 'project.project'

    custom_volunteer_detail_ids = fields.One2many(
        'volunteer.working.details', 
        'custom_project_id', 
        string='Volunteer Working Details',
        copy=True
    )
    custom_volunteer_ids = fields.Many2many(
        'res.partner',
        string='Volunteers',
        required=False,
        copy=True
    )

    def action_volunteer_details(self):
        action = self.env.ref('volunteers_donors_non_profit.action_volunteer_working_details').sudo().read()[0]
        action['domain'] = [('id', 'in', self.custom_volunteer_detail_ids.ids)]
        return action

class Task(models.Model):
    _inherit = "project.task"

    task_volunteer_ids = fields.Many2many(
        'res.partner',
        string='Volunteer',
        required=False,
        copy=True
    )

    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
