# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ResPartner(models.Model):
    
    _inherit = 'res.partner'

    is_volunteer = fields.Boolean(
        string="Is Volunteer?",
        copy=True
    )
    is_donors = fields.Boolean(
        string="Is Donor?",
        copy=True
    )
    res_volunteer_type_id = fields.Many2one(
        'volunteer.type', 
        string="Volunteer Type",
        copy=True
    )
    res_donor_type_id = fields.Many2one(
        'donor.type',
        string="Donor Type",
        copy=True
    )
    res_volunteer_skill_ids = fields.Many2many(
        'volunteer.skills',
        string='Volunteer Skills',
        copy=True
    )