from odoo import http
from odoo.http import request
from datetime import date
from odoo.exceptions import UserError

class CampaignController(http.Controller):

    @http.route(['/campaign/list'], type="http", auth="public", website=True, sitemap=False)
    def list(self, **kwargs): 
        print(">>>>>>>>>>>>>>>>>>>>>>>")
        campaigns = request.env['volunteer.campaign'].sudo().search([('published','=', 'true')])
        print("=====", campaigns)
        return request.render('volunteers_donors_non_profit.website_campaigns', {"data": campaigns})

    @http.route(['/campaign/detail/<int:campaign_id>'], type="http", auth="public", website=True, sitemap=False)
    def detail(self, campaign_id, **kwargs): 
        # kwargs['id']
        campaign = request.env['volunteer.campaign'].browse(campaign_id);
        return request.render('volunteers_donors_non_profit.website_campaign_detail', {"campaign": campaign})
    
    @http.route(['/campaign/donate/<int:campaign_id>'], type="http", auth="public", website=True, sitemap=False)
    def donate(self, campaign_id, **kwargs): 

        # success = "0";
        # Build contact object
        amount = kwargs['amount']

        contact = {
            "name": kwargs['name'],
            "complete_name": kwargs['name'],
            "email": kwargs['email'],
            "mobile": kwargs['mobile'],
            "city": kwargs['city'],
            "active": True,
            "is_donors": True,
            'company_id': 1 # Default company id
        }

        # Create contact data in res.partner model
        created_contact = request.env["res.partner"].sudo().create(contact);
        # vendor = request.env['res.partner'].browse(created_contact.id);

        # Get journal data
        journal = request.env['account.journal'].sudo().search([('code', '=', 'BNK1')])

        if not journal:
            raise UserError('No default journal is available for bill')
        else:

            # Get selected users currency
            company = request.env['res.company'].browse(1)

            # Get default bill journal object
            # Outstanding - Local: 101403, Server: 100203
            # Destination - Local: 121000, Server: 100400
            account_outstanding = request.env['account.account'].sudo().search([('code','=', 100203)])
            account_destination = request.env['account.account'].sudo().search([('code','=', 100400)])

            acc_payment_data = {
                # 'move_id': created_acc_move.id,
                'payment_method_id': 1,
                'currency_id': company.currency_id.id,
                'partner_id': created_contact.id,
                'outstanding_account_id': account_outstanding.id, #44,
                'destination_account_id': account_destination.id, #6,
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'amount': amount,
                'journal_id': journal.id
                # 'amount_company_currency_signed': amount
            }
            acc_payment_model = request.env['account.payment']
            acc_payment_inserted = acc_payment_model.create(acc_payment_data)

            # Create bill for the contact_id. We will share this bill as a receipt with donor
            today = date.today().strftime('%Y-%m-%d')
            acc_move_data = {
                # 'move_type': 'in_invoice',
                'move_type': 'entry',
                'invoice_origin': 'External API',
                'journal_id': journal.id,
                'partner_id': created_contact.id,
                'invoice_date': today,
                'invoice_date_due': today,
                'amount_total': amount,
                'payment_id': acc_payment_inserted.id,
                'invoice_line_ids': [(0,0,{
                    'name': created_contact.name,
                    'account_id': journal.default_account_id.id,
                    'quantity': 1
                })],
            }

            # Insert data in both "account_move" & "account_move_line" tables
            acc_move_model = request.env['account.move']
            created_acc_move = acc_move_model.create(acc_move_data)
            
            # Posting payment that we created in the 1st step
            # acc_payment_inserted.action_post()

            # acc_payment_posted = request.env['account.move'].sudo().search([('name','=', acc_payment_inserted.name)])

            # <> Create campaign payment data

            campaign_payment_data = {
                'partner_id': created_contact.id,
                'volunteer_campaign_id':campaign_id,
                'amount': amount,
                'acc_move_id': created_acc_move.id,
            }
    
            campaign_payment_model = request.env['volunteer.campaign.payment']
            campaign_payment_model.create(campaign_payment_data)
            print("================== Campaign Payment Created ==================")
            # </>

            return request.render('volunteers_donors_non_profit.website_campaign_donation_success', {})
    
    @http.route(['/campaign/payment/success'], type="http", auth="public", website=True, sitemap=False)
    def payment_success(self, **kwargs): 
        return request.render('volunteers_donors_non_profit.website_campaign_donation_success', {})