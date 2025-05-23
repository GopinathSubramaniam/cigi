# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ResPartner(models.Model):
    
    _inherit = 'res.partner'

    campaign_count = fields.Integer('# Campaigns', compute='compute_campaign_count', store=False)

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
        string="Resource Type",
        copy=True
    )
    res_donor_type_id = fields.Many2one(
        'donor.type',
        string="Donor Type",
        copy=True
    )
    res_volunteer_skill_ids = fields.Many2many(
        'volunteer.skills',
        string='Resource Skills',
        copy=True
    )

    # <> New Fields
    gender = fields.Selection([
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other')
    ], string="Gender", copy=True)

    qualification = fields.Char(string="Highest Qualification", copy=True)
    specialization = fields.Char(string="Specialization", copy=True)
    notes = fields.Text(string="Volunteer Notes")


    mobile_country_code = fields.Char(string="Country Code", copy=True)
    phone_country_code = fields.Char(string="Country Code", copy=True)

    pan_number = fields.Char(string="PAN Number", copy=True)

    # </>

    def action_custom_campaign(self):
        action = self.env["ir.actions.actions"]._for_xml_id("volunteers_donors_non_profit.action_custom_campaign")
        action['context'] = {}
        action['domain'] = [('volunteer_campaign_payment_ids.partner_id', 'child_of', self.ids)]
        return action

    
    def compute_campaign_count(self):
        self.campaign_count = 0
        for partner in self:
            partner.campaign_count = self.env['volunteer.campaign'].search_count([('volunteer_campaign_payment_ids.partner_id', 'child_of', partner.ids)])


