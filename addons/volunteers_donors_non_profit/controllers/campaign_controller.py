from datetime import date, datetime

from werkzeug.utils import redirect

import odoo.addons.payment.utils as payment_utils
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request


class CampaignController(http.Controller):

    @http.route(['/campaign/list'], type="http", auth="public", website=True, sitemap=False)
    def list(self, **kwargs): 
        campaigns = request.env['volunteer.campaign'].sudo().search([('published','=', 'true')])
        return request.render('volunteers_donors_non_profit.website_campaigns', {"data": campaigns})

    @http.route(['/campaign/detail/<int:campaign_id>'], type="http", auth="public", website=True, sitemap=False)
    def detail(self, campaign_id, **kwargs): 
        # kwargs['id']
        campaign = request.env['volunteer.campaign'].browse(campaign_id);
        return request.render('volunteers_donors_non_profit.website_campaign_detail', {"campaign": campaign})
    
    # This method will be triggered when the "Donate" button is clicked
    # and will be redirected to the payment page
    @http.route(['/campaign/donate/<int:campaign_id>'], type="http", auth="public", website=True, sitemap=False, csrf=False)
    def donate(self, campaign_id, **kwargs): 

        name = kwargs['name']
        email = kwargs['email']
        mobile = kwargs['mobile']
        city = kwargs['city']
        id_number = kwargs['id_number']
        amount = kwargs['amount']

        contact = {
            "name": name,
            "complete_name": name,
            "email": email,
            "mobile": mobile,
            "city": city,
            "comment": id_number,
            "active": True,
            "is_donors": True,
            'company_id': 1 # Default company id
        }

        # Create contact data in res.partner model
        created_contact = request.env["res.partner"].sudo().create(contact);

        # 2024100409_23_2
        order_id = ('%s_%s_%s' % (datetime.now().strftime('%Y%m%d%H'), created_contact.id, campaign_id))

        # order_id, name, amount, email, phone, desc, callback_url
        callbackurl = payment_utils.get_payment_donation_callback()+order_id
        payment_url = request.env['payment.method']._redirect_to_payment_page(order_id, name, amount, email, mobile, 'Donation', callbackurl)
        return redirect(payment_url)
    
    @http.route(['/campaign/payment/success/<string:return_val>'], type="http", auth="public", website=True, sitemap=False, csrf=False)
    def payment_success(self, return_val): 
        cust_payments = request.env['account.payment'].search([('ref', '=', return_val)])
        if len(cust_payments) == 0:
            # Checking payment status
            payload = {'order_id': return_val}
            jsonres = request.env['payment.method']._call_order_status_api(payload)
            print('Status = ', jsonres)
            
            if(jsonres['status'] == 'CHARGED'):
                return_vals = return_val.split('_')
                contact_id = return_vals[1]
                campaign_id = return_vals[2]
                
                contact = request.env['res.partner'].browse(int(contact_id))
                paid_amount = jsonres['amount']

                # Create bill for the contact_id. We will share this bill as a receipt with donor
                today = date.today().strftime('%Y-%m-%d')
                cust_payment = request.env['payment.method']._create_payment_in_account(return_val, contact.id, today, paid_amount)

                # <> Create campaign payment data
                campaign_payment_data = {
                    'partner_id': contact.id,
                    'volunteer_campaign_id':campaign_id,
                    'amount': paid_amount,
                    'cust_payment_id': cust_payment.id,
                }
                campaign_payment_model = request.env['volunteer.campaign.payment']
                campaign_payment_model.create(campaign_payment_data)
                print("================== Campaign Payment Created ==================")
                # </>

                return request.render('volunteers_donors_non_profit.website_campaign_donation_success', {})
            else:
                return request.render("website_event.payment_failed")
        else:
            return request.render("website_event.order_alread_created", {'order_id': return_val})