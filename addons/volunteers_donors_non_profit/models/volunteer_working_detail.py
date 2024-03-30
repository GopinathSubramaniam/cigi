# -*- coding: utf-8 -*-

from odoo import models, fields, api

class VolunteerDetails(models.Model):
    _name = 'volunteer.working.details'
    _description = 'Volunteer Details'

    volunteer_id = fields.Many2one(
        'res.partner', 
        string="Volunteer",
        copy=True,
        domain="[('is_volunteer', '=', True)]",
        required=True
    ) 
    volunteer_skill_ids = fields.Many2many(
        'volunteer.skills',
        string='Volunteer Skill',
        required=True,
        copy=True
    )
    volunteer_type_id = fields.Many2one(
        'volunteer.type', 
        string="Volunteer Type",
        copy=True,
        required=True
    )
    start_date = fields.Date(
        string="Start Date",
        default=fields.Date.today(),
        required=True,
        copy=True
    )
    end_date = fields.Date(
        string="End Date",
        default=fields.Date.today(),
        required=True,
        copy=True
    )
    description = fields.Text(
        string="Description",
        required=True,
        copy=True
    )
    custom_project_id = fields.Many2one(
        'project.project', 
        string="Project",
        copy=True
    )

    @api.onchange('volunteer_id')
    def set_volunteer_skill_custom(self):
        for rec in self:
            rec.volunteer_type_id = rec.volunteer_id.res_volunteer_type_id.id
            rec.volunteer_skill_ids = rec.volunteer_id.res_volunteer_skill_ids.ids
            if rec.volunteer_id.res_volunteer_type_id:
                rec.description = rec.volunteer_id.name + '-' + rec.volunteer_id.res_volunteer_type_id.name
            else:
                rec.description = rec.volunteer_id.name 
