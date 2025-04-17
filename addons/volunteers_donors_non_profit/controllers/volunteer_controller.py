
import base64
import json
import random
import re
import traceback

from odoo import http
from odoo.http import Response, request
from odoo.tools import html2plaintext

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


class VolunteerController(http.Controller):

    @http.route('/web/volunteer/form', type="http", auth="public", website=True) 
    def volunteer_form(self, **kwargs):
        qual = request.env["hr.skill.type"].sudo().search([('name', '=', 'qualification')], limit=1)
        qualifications = request.env["hr.skill"].sudo().search([('skill_type_id', '=', qual.id)])

        return request.render('volunteers_donors_non_profit.volunteer_form', {'qualifications': qualifications})
    
    @http.route('/web/volunteer/send_otp', type="http", auth="public", website=True, methods=['POST'], csrf=False)
    def send_otp(self, **kwargs):
        json_data = json.loads(request.httprequest.data)
        email = json_data.get('email')
        if not email or not is_valid_email(email):
            return request.make_response(json.dumps({'error': 'Invalid email format'}), headers=[('Content-Type','application/json')])

        print('Sending OTP to ', email)
        otp = random.randint(100000, 999999)
        body_html = ('Dear Volunteer,<br/><br/>OTP for your volunteer email verification is %s.<br/><br/>This OTP will expire after 4hrs. <br/><br/>Thank you.' % (otp))
        mail_values = {
            'subject': 'Volunteer Email Verification OTP',
            'body_html': body_html,
            'email_to': email,
            'email_from': 'CIGI<cigicrm@cigi.org>',
            'email_cc': False,
            'auto_delete': True,
        }
        mail = request.env['mail.mail'].sudo().create(mail_values)
        mail.send()

        res = {'email': email, 'otp': otp}
        cont = request.env["res.partner"].sudo().search([('email', '=', email)], limit=1)
        cont_data = cont.read(['id', 'name', 'gender', 'email', 'phone', 'mobile', 'street', 'city', 'state_id', 'country_id', 'comment', 'company_name', 'qualification', 'specialization', 'website', 'function', 'res_volunteer_type_id', 'res_volunteer_skill_ids'])
        data = cont_data[0] if cont_data else None
        if data is not None:
            skills = request.env["volunteer.skills"].sudo().search([('id', 'in', data['res_volunteer_skill_ids'])])
            skill_names = [s.name for s in skills]
            data['volunteer_skill_names'] = ','.join(skill_names)
            res['data'] = data

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
                tag_ids = [tag.id]

                name = kwargs['name']
                gender = kwargs['gender']
                mobile_country_code = kwargs['mobile_country_code']
                mobile = ('%s %s' % (mobile_country_code, kwargs['mobile']))
                phone_country_code = kwargs['phone_country_code']
                phone = ('%s %s' % (phone_country_code, kwargs['phone']))
                street = kwargs['street']
                state_id = kwargs['state_id']
                city = kwargs['city']
                country_id = kwargs['country_id']
                comment = html2plaintext(kwargs.get('comment',''))
                company_name = kwargs['company_name']
                qualification = kwargs['qualification']
                specialization = kwargs['specialization']
                website = kwargs['website']
                function = kwargs['function']
                # res_volunteer_type_id = kwargs['res_volunteer_type_id']
                res_volunteer_skill_ids_str = kwargs.get('res_volunteer_skill_ids')
                res_volunteer_skill_ids = list(map(int, res_volunteer_skill_ids_str.split(',')))
                contact_picture = kwargs.get('contact_picture')
                
                contact = {
                            "name": name,
                            "complete_name": name,
                            "company_name" : company_name,
                            "gender": gender,
                            "email": email,
                            "phone": phone,
                            "mobile_country_code": mobile_country_code,
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
                            # "res_volunteer_type_id": int(res_volunteer_type_id),
                            "res_volunteer_skill_ids": res_volunteer_skill_ids,
                            "category_id": [(6, 0, tag_ids)] 
                        }
                cont = request.env["res.partner"].sudo().search([('email', '=', email)], limit=1)
                
                # <> Profile pic upload
                base64_data = None
                if contact_picture:
                    image_data = contact_picture.read()
                    base64_data = base64.b64encode(image_data)
                # </>

                if not cont:
                    contact['active'] = True
                    contact['company_id'] = 1
                    if base64_data is not None:
                        contact['image_1920'] = base64_data

                    request.env["res.partner"].sudo().create(contact)
                    res = {'success_msg': 'Registered Successfully'}
                else:
                    contact_tags = cont.category_id
                    for t in contact_tags:
                        tag_ids.append(t.id)
                    
                    cont['category_id'] = [(6, 0, tag_ids)] 

                    if base64_data is not None:
                        cont['image_1920'] = base64_data

                    cont.write(contact)

                    base_url = request.env['ir.config_parameter'].get_param('web.base.url')
                    
                    res = {'success_msg': 'Updated Successfully', 'redirect_url': f'{base_url}/web/volunteer/form' }
                    return request.render('volunteers_donors_non_profit.volunteer_form', res)
        
        except Exception as e:
            print('Error;', e)
            traceback.print_exc()
            res = {'err_msg': 'Error Occurred'}
        
        return request.render('volunteers_donors_non_profit.volunteer_form', res)
    
    @http.route('/web/volunteer/get_profile_picture/<int:partner_id>', type="http", auth="public", website=True, methods=['GET'])
    def get_profile_picture(self, partner_id, **kwargs):
        # Fetch the partner record using the partner_id
        partner = request.env['res.partner'].sudo().browse(partner_id)

        if partner.exists():
            # Get the profile picture from the partner's image_1920 field
            image_data = partner.image_1920
            if image_data:
                # Return the image as a response with the correct MIME type
                return Response(
                    base64.b64decode(image_data),
                    content_type='image/png',  # Adjust MIME type if it's JPEG, etc.
                    status=200
                )
            else:
                return Response("No image available", status=404)
        else:
            return Response("Partner not found", status=404)
    