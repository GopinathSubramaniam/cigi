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

    payment_ref_num = fields.Char(string='HDFC Ref', compute='get_payment_info', store=False)
    pan_num = fields.Char(string='PAN', store=False)

    notes = fields.Text(string="Notes") 

    def get_invoice_num(self):
        for rec in self:
            rec.invoice_num = rec.cust_payment_id.move_id.name

    def get_payment_info(self):
        for rec in self:
            if rec.cust_payment_id and rec.cust_payment_id.move_id and rec.cust_payment_id.move_id.ref:
                print('Value = ', rec.cust_payment_id.move_id.ref)
                splitted = rec.cust_payment_id.move_id.ref.split(',')
                for val in splitted:
                    key = val.split(':')[0] # Getting key from the string
                    if 'Payment Ref' in key:
                        rec.payment_ref_num = val.split(':')[1].strip()  # Getting payment ref number from the string
                    
                    if 'PAN' in key:
                        rec.pan_num = val.split(':')[1].strip()# Getting PAN number from the string

    