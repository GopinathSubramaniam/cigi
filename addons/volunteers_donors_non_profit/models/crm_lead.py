# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class Lead(models.Model):
    _inherit = 'crm.lead'

    custom_volunteer_type_id = fields.Many2one(
        'volunteer.type', 
        string="Volunteer Type",
        copy=True
    )
    custom_donor_type_id = fields.Many2one(
        'donor.type',
        string="Donor Type",
        copy=True
    )
    custom_volunteer_skill_ids = fields.Many2many(
        'volunteer.skills',
        string='Volunteer Skills',
        copy=True
    )
    
    @api.onchange('partner_id')
    def custom_onchange_partner_id(self):
        self.custom_donor_type_id = self.partner_id.res_donor_type_id.id
        self.custom_volunteer_type_id = self.partner_id.res_volunteer_type_id.id
        self.custom_volunteer_skill_ids = self.partner_id.res_volunteer_skill_ids.ids
