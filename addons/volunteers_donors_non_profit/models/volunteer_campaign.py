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

    fund_received_percent = fields.Float(
        default = 0.00,
        store = False,
        compute = '_calculate_percent'
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

    youtube_url = fields.Char(
        string="Youtube URL",
        required=False
    )

    description = fields.Html(
        string="Description",
        required=True
    )

    # Get all associated campaigns objects
    volunteer_campaign_payment_ids = fields.One2many(
        'volunteer.campaign.payment',
        'volunteer_campaign_id',
        string='Payments',
        copy=False,
    )

    def _calculate_percent(self):
        print('Calculate Received Fund Percentage')
        for o in self:
            if o.fund_need > 0:
                o.fund_received_percent = round((o.fund_received / o.fund_need ) * 100, 2);
            else:
                o.fund_received_percent = 0.00

