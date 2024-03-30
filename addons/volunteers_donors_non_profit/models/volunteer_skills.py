# -*- coding: utf-8 -*-

from odoo import models, fields, api

class VolunteerSkills(models.Model):
    _name = 'volunteer.skills'
    _description = 'Volunteer Skills'

    name = fields.Char(
        string="Name",
        required=True
    )
    code = fields.Char(
        string="Code",
        required=True
    )
    note = fields.Text(
        string="Internal Notes"
    )
    color = fields.Integer(
        string='Color Index'
    )
    
