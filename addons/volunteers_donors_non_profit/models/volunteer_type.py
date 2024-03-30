# -*- coding: utf-8 -*-

from odoo import models, fields, api

class VolunteerType(models.Model):
    _name = 'volunteer.type'
    _description = 'VolunteerType'

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
    
