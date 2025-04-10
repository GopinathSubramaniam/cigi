from odoo import models, fields, api
import math
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class Campaign(models.Model):
    _name = 'volunteer.campaign'
    _description = "Campaign"


    campaign_name = fields.Char(
        string = "Campaign Name",
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

    fund_need = fields.Float(
        string="Fund Need",
        digits=(12,2),
        default=0.00,
        required = True
    )

    fund_received = fields.Float(
        string="Fund Received", 
        digits=(12,2),
        store = False,
        compute = "_fund_received"
    )

    fund_received_percent = fields.Float(
        default = 0.00,
        store = False,
        compute = '_calculate_percent'
    )

    end_date = fields.Datetime(
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

    is_expired = fields.Boolean(
        default = False,
        store = False,
        compute = '_is_expired'
    )

    def download_donations_excel(self):
        campaign_id = self.id
        _logger.info(f'Campaign Id = {campaign_id}')
        return {
            'type': 'ir.actions.act_url',
            'url': f'/campaign/download/donations/{self.id}',
            'target': 'new',
        }
    
    def _fund_received(self):
        self.fund_received = 0.00
        for c in self:
            data = self.env['volunteer.campaign.payment'].sudo().search([('volunteer_campaign_id', '=', c.id)])
            if data is not None:
                for o in data:
                    c.fund_received += o.amount
    
    def _calculate_percent(self):
        for o in self:
            if o.fund_need > 0:
                o.fund_received_percent = math.ceil((o.fund_received / o.fund_need ) * 100)
            else:
                o.fund_received_percent = 0.00

    def _is_expired(self):
        for o in self:
            o.is_expired = datetime.now() > o.end_date
