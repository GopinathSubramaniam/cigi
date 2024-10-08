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

    acc_move_id = fields.Many2one(
        'account.move',
        string="Account Payment",
        index=True,
        readonly=True,
        auto_join=True,
        ondelete="cascade",
        required=True,
    )
    
    user_email = fields.Char(string='Email', related='partner_id.email')
    user_mobile = fields.Char(string='Mobile', related='partner_id.mobile')
    # acc_payment_name = fields.Char(string='Payment Name', related='acc_move_id.name')

    invoice_num = fields.Char(compute='get_invoice_num', string='Payment Number', store=False)

    def get_invoice_num(self):
        for rec in self:
            print('Payment Id = ', rec.acc_move_id.name)
            rec.invoice_num = rec.acc_move_id.name