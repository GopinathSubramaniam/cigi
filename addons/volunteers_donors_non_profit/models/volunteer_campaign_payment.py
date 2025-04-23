from odoo import _, api, fields, models

class VolunteerCampaignPayment(models.Model):
    _name = 'volunteer.campaign.payment'
    _description = 'Volunteers campaign payments'

    partner_id = fields.Many2one('res.partner', string="Customer")

    volunteer_campaign_id = fields.Many2one(
        'volunteer.campaign',
        string="Campaign",
        index=True,
        readonly=True,
        auto_join=True,
        ondelete="cascade",
        required=True,
    )

    amount = fields.Float(
        string="Amount",
        digits=(12,2),
        default = 0.00,
    )

    cust_payment_id = fields.Many2one(
        'account.payment',
        string="Payment",
        index=True,
        readonly=True,
        auto_join=True,
        ondelete="cascade",
        required=True,
    )

    user_email = fields.Char(string='Email', related='partner_id.email')
    user_mobile = fields.Char(string='Mobile', related='partner_id.mobile')

    invoice_num = fields.Char(compute='get_invoice_num', string='Payment Number', store=False)

    payment_ref_num = fields.Char(string='Payment Ref', related='cust_payment_id.payment_ref')
    pan_num = fields.Char(string='PAN', related='partner_id.pan_number')

    notes = fields.Text(string="Notes") 

    def get_invoice_num(self):
        for rec in self:
            rec.invoice_num = rec.cust_payment_id.move_id.name

    
    