
from odoo import models
import base64
import re

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _create_payment_in_account(self, ref_val, contact_id, payment_date, amount):
      
        journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
        acc_payment_method = self.env['account.payment.method'].search([('code', '=', 'manual'), ('payment_type', '=', 'inbound')], limit=1)
        campaign_id = ref_val.split('_')[2]
        campaign = self.env['volunteer.campaign'].sudo().browse(int(campaign_id))
        contact = self.env['res.partner'].sudo().browse(int(contact_id))

        print(contact)
        # <> Removing the html tags 
        print(contact.comment)
        comt = ''
        if(contact.comment):
            clean = re.compile('<.*?>')
            comt =  re.sub(clean, '', contact.comment)
        # </>

        payment_vals = {
            'partner_id': contact_id,  # Customer/Vendor ID
            'amount': amount,  # Payment amount
            'payment_type': 'inbound',  # 'inbound' for customer payments, 'outbound' for vendor payments
            'payment_method_id': acc_payment_method.id,  # Payment method (like manual, bank, etc.)
            'journal_id': journal.id,  # The journal for the payment (e.g., bank journal)
            'currency_id': journal.company_id.currency_id.id,  # Currency in which payment is made
            'partner_type': 'customer',  # 'customer' or 'supplier'
            'ref': ('%s:%s, %s:%s, %s' % ('Payment Ref', ref_val, 'Campaign Name', campaign.campaign_name, comt)),  # A reference note or description
            'date': payment_date,  # The payment date
        }
        print('Payment Ref = ', payment_vals['ref'])
        payment = self.env['account.payment'].create(payment_vals)
        payment.sudo().action_post()
       
        pdf_content, _ = self.env['ir.actions.report'].sudo()._render_qweb_pdf("volunteers_donors_non_profit.custom_payment_receipt_report", payment.id)
        
        attachment = self.env['ir.attachment'].sudo().create({
            'name': 'Payment Receipt.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'account.payment',
            'res_id': payment.id,
            'mimetype': 'application/pdf'
        })
        
        mail_template = """Dear Donor,<br/><br/>
                            Thank you for your generous support of CIGI. Your contribution plays a vital role in advancing our mission, and we assure you that every rupee will be used to make a meaningful impact.<br/><br/>
                            Please find your payment receipt attached for your reference. If there are any discrepancies with your online payment, we will reach out to you within seven working days to resolve the issue. <br/><br/>
                            We truly appreciate your generosity and commitment to our cause. <br/><br/>
                            Best Regards,<br/>
                            Team CIGI
                        """

        mail_values = {
            'subject': 'Thank You for Your Support',
            'body_html': mail_template,
            'email_to': payment.partner_id.email,
            'email_from': 'CIGI <cigicrm@cigi.org>',
            'reply_to' : 'helpdesk@cigi.org',
            'email_cc': False,
            'auto_delete': True,
            'attachment_ids': [(6, 0, [attachment.id])],
        }
        mail = self.env['mail.mail'].sudo().create(mail_values)
        mail.send()

        print("Payment Attachment Mail Sent")
        
        return payment
