# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DonorType(models.Model):
    _name = 'donor.type'
    _description = 'DonorType'

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
    
