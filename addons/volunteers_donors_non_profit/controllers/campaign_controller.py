import json
from datetime import date, datetime

from werkzeug.utils import redirect

import odoo.addons.payment.utils as payment_utils
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request
import traceback


class CampaignController(http.Controller):

    @http.route(['/campaign/list'], type="http", auth="public", website=True, sitemap=False)
    def list(self, **kwargs): 
        campaigns = request.env['volunteer.campaign'].sudo().search([('published','=', 'true')])
        return request.render('volunteers_donors_non_profit.website_campaigns', {"data": campaigns})

    @http.route(['/campaign/detail/<int:campaign_id>'], type="http", auth="public", website=True, sitemap=False)
    def detail(self, campaign_id, **kwargs): 
        # kwargs['id']
        campaign = request.env['volunteer.campaign'].browse(campaign_id);
        print('2nd Image = ', campaign.second_image)
        return request.render('volunteers_donors_non_profit.website_campaign_detail', {"campaign": campaign})
    
    # This method will be triggered when the "Donate" button is clicked
    # and will be redirected to the payment page
    @http.route(['/campaign/donate/<int:campaign_id>'], type="http", auth="public", website=True, sitemap=False, csrf=False)
    def donate(self, campaign_id, **kwargs): 
        
        try:
            amount = kwargs['amount']
            name = kwargs['name']
            email = kwargs['email']
            mobile = kwargs['mobile']
            notes = kwargs['notes']

            # Validate notes: max 100 words
            word_count = len([word for word in notes.strip().split() if word])
            if word_count > 100:
                campaign = request.env['volunteer.campaign'].browse(campaign_id)
                return request.render('volunteers_donors_non_profit.website_campaign_detail', {
                    "campaign": campaign,
                    "error_message": "Notes cannot exceed 100 words. Please shorten your message.",
                    "form_data": kwargs,  # Pass the form data back to the front-end
                    "is_error": True,  # Flag for error handling
                })

            # Country of residence
            country_of_residence = False
            if kwargs['country_of_residence']:
                country_of_residence = request.env['res.country'].sudo().browse(int(kwargs['country_of_residence']))
            
            id_number = kwargs['id_number'] # PAN Number
            
            street = kwargs['address']
            state_id = kwargs['state_id']
            city = kwargs['city']
            zip = kwargs['zip']

            # Default country
            country = request.env['res.country'].sudo().search([('code', '=', 'IN')], limit=1)
            if country_of_residence:
                country = country_of_residence

            tag = request.env['res.partner.category'].search([('name', '=', 'Donor')], limit=1)
            if not tag:
                tag = request.env['res.partner.category'].create({
                    'name': 'Donor'
                })

            # <> Create a new contact If the contact is not exists
            existing_cont = request.env["res.partner"].sudo().search([('email', '=', email)], limit=1)
            print('Comment = ', existing_cont.comment)
            contact = {
                    "name": name,
                    "complete_name": name,
                    "email": email,
                    "mobile": mobile,
                    "city": city,
                    "country_id": country.id,
                    "state_id": state_id,
                    "street": street,
                    # "comment": ('%s:%s, %s: %s' % ('Country of Residence', country_of_residence_name, 'PAN', id_number)),
                    "pan_number": id_number,
                    "active": True,
                    "is_donors": True,
                    'company_id': 1, # Default company id
                    'category_id': [(6, 0, [tag.id])] ,
                    'zip': zip
                }
                
            if not existing_cont:
                existing_cont = request.env["res.partner"].sudo().create(contact) # Create a new contact
            else:
                existing_cont.write(contact) # Update existing contact
            # </>

            # 2024100409_23_2
            order_id = ('%s_%s_%s' % (datetime.now().strftime('%Y%m%d%H%M'), existing_cont.id, campaign_id))

            # order_id, name, amount, email, phone, desc, callback_url
            callbackurl = payment_utils.get_payment_donation_callback()+order_id
            donation_note = 'Donation'
            if notes:
                donation_note = f'{donation_note}~{notes}'

            payment_url = request.env['payment.method']._redirect_to_payment_page(order_id, name, amount, email, mobile, donation_note, callbackurl)
            print('Payment URL = ', payment_url)
            return redirect(payment_url)
        except Exception as e:
           print(e)
           print(traceback.format_exc())
           raise UserError(f"Something went wrong. Please try again later")
    
    @http.route(['/campaign/payment/success/<string:return_val>'], type="http", auth="public", website=True, sitemap=False, csrf=False)
    def payment_success(self, return_val): 
        cust_payments = request.env['account.payment'].search([('ref', 'ilike', return_val)])
        print('return_val = ', return_val)
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
                notes = jsonres['metadata']['payment_page_sdk_payload']['description']
                splitted = notes.split('~')
                if splitted and len(splitted) > 1:
                    notes = splitted[1]

                # Create bill for the contact_id. We will share this bill as a receipt with donor
                today = date.today().strftime('%Y-%m-%d')
                # cust_payment = request.env['payment.method']._create_payment_in_account(return_val, contact.id, today, paid_amount)
                cust_payment = request.env['account.payment']._create_payment_in_account(return_val, contact.id, today, paid_amount)

                # <> Create campaign payment data
                campaign_payment_data = {
                    'partner_id': contact.id,
                    'volunteer_campaign_id':campaign_id,
                    'amount': paid_amount,
                    'cust_payment_id': cust_payment.id,
                    'notes': notes,
                }
                campaign_payment_model = request.env['volunteer.campaign.payment']
                campaign_payment_model.create(campaign_payment_data)
                
                # </>
                request.session.pop('donation_note', None)
                return request.render('volunteers_donors_non_profit.website_campaign_donation_success', {})
            else:
                return request.render("website_event.payment_failed")
        else:
            return request.render("website_event.order_alread_created", {'order_id': return_val})
        

    @http.route('/app/get_states', type='http', auth="public", website=True)
    def get_states(self, country_id):
        print('Country Id = ', country_id)
        if country_id:
            states = request.env['res.country.state'].sudo().search([('country_id', '=', int(country_id))])
            state_list = [{'id': state.id, 'name': state.name} for state in states]
            return request.make_response(json.dumps({'states': state_list}), headers=[('Content-Type', 'application/json')])
        return request.make_response(json.dumps({'states': []}), headers=[('Content-Type', 'application/json')])
    
    @http.route('/app/get_states_by_country_code', type='http', auth="public", website=True)
    def get_states(self, country_code):
        if country_code:
            country = request.env['res.country'].sudo().search([('code', '=', country_code)])
            states = request.env['res.country.state'].sudo().search([('country_id', '=', country.id)])
            state_list = [{'id': state.id, 'name': state.name} for state in states]
            return request.make_response(json.dumps({'states': state_list}), headers=[('Content-Type', 'application/json')])
        return request.make_response(json.dumps({'states': []}), headers=[('Content-Type', 'application/json')])

    
    @http.route(['/campaign/download/donations/<int:campaign_id>'], type="http", auth="public", website=True, sitemap=False)
    def download_donations(self, campaign_id, **kwargs): 
        excel_file = request.env['export.donation.wizard'].export_donations(campaign_id)
        return request.make_response(
            excel_file,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', f'attachment; filename="donations_list.xlsx"')
            ]
        )
    