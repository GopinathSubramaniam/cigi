from odoo import http
from odoo.http import request
from datetime import date
from odoo.exceptions import UserError

class CampaignController(http.Controller):

    @http.route(['/campaign/list'], type="http", auth="public", website=True, sitemap=False)
    def list(self, **kwargs): 
        campaigns = request.env['volunteer.campaign'].sudo().search([])
        return request.render('volunteers_donors_non_profit.website_campaigns', {"data": campaigns})

    @http.route(['/campaign/detail/<int:campaign_id>'], type="http", auth="public", website=True, sitemap=False)
    def detail(self, campaign_id, **kwargs): 
        # kwargs['id']
        campaign = request.env['volunteer.campaign'].browse(campaign_id);
        return request.render('volunteers_donors_non_profit.website_campaign_detail', {"campaign": campaign})
    
    @http.route(['/campaign/donate/<int:campaign_id>'], type="http", auth="public", website=True, sitemap=False)
    def donate(self, campaign_id, **kwargs): 

        success = "0";
        # Build contact object
        contact = {
            "name": kwargs['name'],
            "complete_name": kwargs['name'],
            "email": kwargs['email'],
            "mobile": kwargs['mobile'],
            "city": kwargs['city'],
            "active": True,
            "is_donors": True,
        };
        
        # Create contact data in res.partner model
        created_contact = request.env["res.partner"].sudo().create(contact);
        # vendor = request.env['res.partner'].browse(created_contact.id);

        # Create bill for the contact_id. We will share this bill as a receipt with donor
        acc_move_model = request.env['account.move'];
        
        
        # Get default bill journal object
        bill_default_account = request.env['account.account'].sudo().search([('code','=', 600000)]);

        if not bill_default_account:
            raise UserError('No default journal is available for bill')
        else:
            inv_data = {
                'move_type': 'in_invoice',
                'invoice_origin': 'External API',
                'partner_id': created_contact.id,
                #  'ref': 'OASAS@',
                'invoice_date': date.today().strftime('%Y-%m-%d'),
                'invoice_line_ids': [(0,0,{
                    'name': created_contact.name,
                    'account_id': bill_default_account.id,
                    'price_unit': 200,
                    'quantity': 1
                })],
            }
            created_bill = acc_move_model.create(inv_data)
            # created_bill.action_invoice_open()

            # Confirm the bill
            # acc_move_model.action_invoice_open(); 
            success = "1";


        return success;