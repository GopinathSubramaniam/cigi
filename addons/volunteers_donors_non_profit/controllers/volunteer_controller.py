
import json
from odoo import http
from odoo.http import request
import random
import traceback

class VolunteerController(http.Controller):

    @http.route('/web/volunteer/form', type="http", auth="public", website=True)
    def volunteer_form(self, **kwargs):

        return request.render('volunteers_donors_non_profit.volunteer_form', {'title': 'Volunteer Form'})
    
    @http.route('/web/volunteer/send_otp', type="http", auth="public", website=True, methods=['POST'], csrf=False)
    def send_otp(self, **kwargs):
        json_data = json.loads(request.httprequest.data)
        email = json_data.get('email')
        print('Sending OTP to ', email)

        otp = random.randint(100000, 999999)
        body_html = ('Dear Volunteer,<br/><br/>OTP for your volunteer email verification is %s.<br/><br/>This OTP will expire after 4hrs. <br/><br/>Thank you.' % (otp))
        mail_values = {
            'subject': 'Volunteer Email Verification OTP',
            'body_html': body_html,
            'email_to': email,
            'email_from': 'erp@cigi.org',
            'email_cc': False,
            'auto_delete': True,
        }
        mail = request.env['mail.mail'].sudo().create(mail_values)
        mail.send()

        res = {'email': email, 'otp': otp}
        cont = request.env["res.partner"].sudo().search([('email', '=', email)], limit=1)
        cont_data = cont.read(['id', 'name', 'gender', 'email', 'phone', 'mobile', 'street', 'city', 'state_id', 'country_id', 'comment', 'company_name', 'qualification', 'specialization', 'website', 'function', 'res_volunteer_type_id'])
        res['data'] = cont_data[0] if cont_data else ''

        return request.make_response(json.dumps(res), headers=[('Content-Type', 'application/json')])
    
    @http.route('/web/volunteer/registration', type="http", auth="public", website=True, methods=['POST', 'GET'])
    def volunteer_registration(self, **kwargs):
        res = {}
        try:
            email = kwargs.get('email')
            
            if email:

                tag = request.env['res.partner.category'].search([('name', '=', 'Volunteer')], limit=1)
                if not tag:
                    tag = request.env['res.partner.category'].create({
                        'name': 'Volunteer'
                    })

                name = kwargs['name']
                gender = kwargs['gender']
                mobile = kwargs['mobile']
                phone = kwargs['phone']
                street = kwargs['street']
                state_id = kwargs['state_id']
                city = kwargs['city']
                country_id = kwargs['country_id']
                comment = kwargs['comment']
                company_name = kwargs['company_name']
                qualification = kwargs['qualification']
                specialization = kwargs['specialization']
                website = kwargs['website']
                function = kwargs['function']
                res_volunteer_type_id = kwargs['res_volunteer_type_id']
                res_volunteer_skill_ids = kwargs.get('res_volunteer_skill_ids', [])
                if isinstance(res_volunteer_skill_ids, str):
                    res_volunteer_skill_ids = [res_volunteer_skill_ids]

                contact = {
                            "name": name,
                            "complete_name": name,
                            "company_name" : company_name,
                            "gender": gender,
                            "email": email,
                            "phone": phone,
                            "mobile": mobile,
                            "city": city,
                            "country_id": int(country_id),
                            "state_id": int(state_id),
                            "street": street,
                            "function": function,
                            "comment": comment,
                            "qualification": qualification,
                            "specialization": specialization,
                            "website": website,
                            "is_volunteer": True,
                            "res_volunteer_type_id": int(res_volunteer_type_id),
                            "res_volunteer_skill_ids": res_volunteer_skill_ids,
                            "category_id": [(6, 0, [tag.id])] 
                        }
                cont = request.env["res.partner"].sudo().search([('email', '=', email)], limit=1)
                
                print('>>>>>>>>>> res_volunteer_skill_ids >>>>>>>>>>>>>')
                print(res_volunteer_skill_ids)
                
                if not cont:
                    contact['active'] = True
                    contact['company_id'] = 1
                    request.env["res.partner"].sudo().create(contact)
                    res = {'success_msg': 'Registered Successfully'}
                else:
                    cont.write(contact)
                    res = {'success_msg': 'Updated Successfully'}
        
        except Exception as e:
            print('Error;', e)
            traceback.print_exc()
            res = {'err_msg': 'Error Occurred'}
        
        return request.render('volunteers_donors_non_profit.volunteer_form', res)
    
    