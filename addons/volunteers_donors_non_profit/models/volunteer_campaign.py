from odoo import models, fields, api

class Campaign(models.Model):
    _name = 'volunteer.campaign'
    _description = "Campaign"

    project_name = fields.Char(
        string = "Project Name",
    )

    campaign_type = fields.Selection([
            ('MEDIC', 'Medical'),
            ('EDU', 'Education'),
            ('MEMORIAL', 'Memorial'),
            ('OTHER', 'Other')
        ], 
        string="Campaign Type",
        required = True
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

    fund_need = fields.Float(
        string="Fund Need",
        digits=(12,2),
        default=0.00,
        required = True
    )

    fund_received = fields.Float(
        string="Fund Received",
        digits=(12,2),
        default = 0.00
    )

    end_date = fields.Date(
        string="Campaign End Date",
        required = True
    )

    # <> Campaign Images
    first_image = fields.Binary(
        string="First Image"
    )
    second_image = fields.Binary(
        string="Second Image"
    )
    third_image = fields.Binary(
        string="Third Image"
    )
    # </> 

    published = fields.Boolean(
        string="Published"
    )

    description = fields.Text(
        string="Description",
        required=True
    )
