from odoo import models, fields, api

class Campaign(models.Model):
    _name = 'campaign'
    _description = "Campaign"

    campaign_type = fields.Selection([
        ('MEDIC', 'Medical'),
        ('EDU', 'Education'),
        ('MEMORIAL', 'Memorial'),
        ('OTHER', 'Other')
    ], 
    string="Campaign Type",
    required = True
    )

    created_for = fields.Selection([
        ('MYSELF', 'MySelf'),
        ('FAMILY', 'Family'),
        ('FRIEND', 'Friend'),
        ('NEIGHBOUR', 'Neighbour'),
        ('OTHER', 'Other')
    ],
    string = "Created For",
    required = True
    )

    beneficiary_name = fields.Char(
        string = "Beneficiary Name",
    )

    title = fields.Char(
        string = "Title",
        required = True
    )
    
    address = fields.Char(
        string = "Address",
        required = True
    )

    mobile = fields.Char(
        string = "Mobile Number",
        required = True
    )

    amount = fields.Float(
        string="Amount",
        digits=(12,2),
        required = True
    )

    end_date = fields.Date(
        string="End Date",
        required = True
    )

    images = fields.Binary(
        string="Image"
    )

    published = fields.Boolean(
        string="Published"
    )

    description = fields.Char(
        string="Description",
        required=True
    )
