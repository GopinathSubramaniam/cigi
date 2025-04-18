import json

import werkzeug
from werkzeug.utils import redirect

import odoo.addons.payment.utils as payment_utils
from odoo import SUPERUSER_ID, _, fields, http
from odoo.exceptions import UserError
from odoo.http import request


class CustomEventController(http.Controller):

    @http.route('/download/event_attendees/<int:event_id>', type='http', auth="user", csrf=False)
    def download_event_attendees(self, event_id, **kwargs):
        excel_file = request.env['export.attendee.wizard'].export_attendees(event_id)
        return request.make_response(
            excel_file,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', f'attachment; filename="attendees_list.xlsx"')
            ]
        )
    
    @http.route('/event/custom_register/<int:event_id>', auth="public", methods=['POST'], website=True)
    def event_registration_page(self, event_id, **kwargs):
        event = request.env['event.event'].sudo().browse(event_id)

        tickets = self._process_tickets_form(event, kwargs)
        
        availability_check = True
        if event.seats_limited:
            ordered_seats = 0
            for ticket in tickets:
                ordered_seats += ticket['quantity']
            if event.seats_available < ordered_seats:
                availability_check = False
        if not tickets:
            return False
        default_first_attendee = {}
        if not request.env.user._is_public():
            default_first_attendee = {
                "name": request.env.user.name,
                "email": request.env.user.email,
                "phone": request.env.user.mobile or request.env.user.phone,
            }
        else:
            visitor = request.env['website.visitor']._get_visitor_from_request()
            if visitor.email:
                default_first_attendee = {
                    "name": visitor.display_name,
                    "email": visitor.email,
                    "phone": visitor.mobile,
                }

        print('Tickets Count = ', tickets[0]['quantity'])
        ticket_per_price = event.event_ticket_ids[0].price if (event.event_ticket_ids and event.event_ticket_ids[0]) else 0.00
        total_amount = round((ticket_per_price * int(tickets[0]['quantity'])), 2)
        return request.render('custom_event.event_custom_registration_template', {
            'total_tickets': len(tickets),
            'total_amount': total_amount,
            'tickets': tickets,
            'event': event,
            'availability_check': availability_check,
            'default_first_attendee': default_first_attendee,
        })

    @http.route('/event/apply_custom_coupon', type='json', auth="public", methods=['POST'])
    def apply_custom_coupon(self, **post):
        data = json.loads(request.httprequest.data)
        promo_code = data.get('coupon_code', '')
        order_amount = data.get('order_amount', 0.00)
        resp = request.env['event.event'].validate_coupon(promo_code, order_amount)
        return resp

    @http.route(['''/event/<model("event.event"):event>/registration/custom_confirm'''], type='http', auth="public", methods=['POST'], website=True)
    def registration_custom_confirm(self, event, **post):
        
        coupon_code = post['coupon_code']
        print('Coupon Code = ', coupon_code)
        del post['coupon_code']
        
        event_event = request.env['event.event']
        registrations_data = self._process_attendees_form(event, post)
        event_ticket_ids = {registration['event_ticket_id'] for registration in registrations_data}
        event_tickets = request.env['event.event.ticket'].browse(event_ticket_ids)
        
        if any(event_ticket.seats_limited and event_ticket.seats_available < len(registrations_data) for event_ticket in event_tickets):
            return request.redirect('/event/%s/register?registration_error_code=insufficient_seats' % event.id)
        
        data = event_event._create_attendees_from_registration_post(event, registrations_data)
        attendees_sudo = data['attendees_sudo']
        contact_id = data['contact_id']
        
        attendee = attendees_sudo[0]
        event_ticket = request.env['event.event.ticket'].browse(attendee.event_ticket_id.id)

        if event_ticket.price is not None and event_ticket.price > 0:

            # AT<Attendee Id>EV<Event Id>TI<Event Ticket Id>
            order_id = ('AT%sEV%sTI%s' % (attendee.id, attendee.event_id.id, attendee.event_ticket_id.id))
            atten_ids = "-".join([str(id) for id in attendees_sudo.ids])

            # request.session[payment_utils.EVENT_PRICE] = event_ticket.price
            # <> Initiate the payment
            visitor = request.env['website.visitor']._get_visitor_from_request()
           
            return_id = ('/%s_%s_%s_%s_%s_%s' % (order_id, atten_ids, attendee.event_id.id, contact_id, visitor.id, coupon_code))
            callback_url = payment_utils.PAYMENT_CALLBACK_URL+return_id
            print('Callback URL = ',callback_url)
            order_amount = (event_ticket.price * len(attendees_sudo))
            
            discount_amount = 0
            if coupon_code is not None and coupon_code != "":
                discount_amount = event_event.get_discount_amount(coupon_code, order_amount)
            
            print('Phone = ', ('' if (attendee.phone is None or attendee.phone is False) else attendee.phone))
            print('Discount Amount = ', discount_amount)
            print('Order Amount = ', order_amount)
            print(event_ticket)
            print('Event Ticket Name = ', event_ticket.name)
            print('Event Name = ',event.name)
            payload = {
                    'order_id': order_id,
                    'amount': round((order_amount - discount_amount), 2),
                    'customer_id': ('CUST_%s_%s' % (attendee.id, order_id)),
                    'customer_email': attendee.email,
                    'customer_phone': ('' if (attendee.phone is None or attendee.phone is False) else attendee.phone),
                    'payment_page_client_id': 'hdfcmaster',
                    'action': "paymentPage",
                    'currency': "INR",
                    'return_url': callback_url,
                    'description': 'Event: ' + event.name + ', Ticket: '+event_ticket.name,
                    'first_name': attendee.name,
                    'last_name': ''
                }
            try:
                jsonres = request.env['payment.method']._call_session_api(payload)
                print(jsonres)
                print(jsonres['payment_links'])
                payment_link = jsonres['payment_links']['web']
                print(payment_link)
                return redirect(payment_link)
            except Exception as e:
                raise UserError("Payment gateway issue. Please try again later.")
            
            # </>
        else: 
            registration_ids = ",".join([str(id) for id in attendees_sudo.ids])
            return request.redirect(('/event/%s/registration/success?' % event.id) + werkzeug.urls.url_encode({'registration_ids': registration_ids}))

    # Customized
    @http.route(['/event/order/success/<string:session_val>'], type="http", auth="public", website=True, sitemap=False, csrf=False)
    def event_order_success(self, session_val): 
        print('Session Value = ', session_val)
        session_vals = session_val.split('_')

        order_id = session_vals[0]
        print('Order Id = ', order_id)
        existing_invoices = request.env['account.move'].search([('invoice_origin', '=', order_id)])
        print('Invoice Length = ', len(existing_invoices))
        # Create invoice only if the invoice is not created already
        if len(existing_invoices) == 0:
            attendees_ids = session_vals[1]
            att_ids = [int(attendees_id) for attendees_id in attendees_ids.split('-')]
            event_id = int(session_vals[2])
            contact_id = int(session_vals[3])
            visitor_id = int(session_vals[4])
            coupon_code = session_vals[5]

            payload = {'order_id': order_id}
            jsonres = request.env['payment.method']._call_order_status_api(payload)
            print('Status = ', jsonres)
            
            # Create the invoice only if the payment status is 'CHARGED'
            if(jsonres['status'] == 'CHARGED'):
                event = request.env['event.event'].browse(event_id)
                attendees_sudo = request.env['event.registration'].sudo().search([
                    ('id', 'in', att_ids),
                    ('event_id', '=', event.id),
                    ('visitor_id', '=', visitor_id),
                ])
            
                # <> Creating SO & Lines when submitting for payment
                event_ticket = request.env['event.event.ticket'].search([('event_id', '=', event_id)], limit=1) # Get event ticket
                loyalty_reward = request.env['event.event'].get_loyal_reward_product_id(coupon_code)
                discount_amount  = request.env['event.event'].get_discount_amount(coupon_code, (event_ticket.price * len(att_ids)))

                order_data = {
                    'name': order_id,
                    'partner_id': contact_id,
                    'partner_invoice_id': contact_id,
                    'partner_shipping_id': contact_id,
                    'order_line': [
                        (0, 0,{
                            'event_id': event_id,
                            'event_ticket_id': event_ticket.id,
                            'product_id': event_ticket.product_id.id,
                            'name': event_ticket.name, #event_ticket.product_id.product_tmpl_id.name['en_US']
                            'product_uom' : event_ticket.product_id.product_tmpl_id.uom_id.id,
                            'product_uom_qty' : len(att_ids),
                            'tax_id': [(6, 0, [])],
                        })
                    ]
                }
                
                so = request.env['sale.order'].with_user(SUPERUSER_ID).create(order_data)

                if coupon_code is not None and coupon_code != "":
                    # Adding coupon in SO
                    request.env['sale.order.line'].create({
                        'order_id': so.id,
                        'product_id': loyalty_reward.discount_line_product_id.id,
                        'product_uom_qty': 1,
                        'price_unit': -discount_amount,  # You can set a specific price if needed
                    })
                
                # <> Update event registrations with sale_order_id and sale_order_line_id
                order_line = request.env['sale.order.line'].search([('order_id', '=', so.id)], limit=1)
                request.env['event.registration'].search([('id', 'in', att_ids)]).update({'sale_order_id': so.id, 'sale_status': 'sold', 'sale_order_line_id': order_line.id})
                
                so.action_confirm() # Confirm SO

                request.env['payment.method']._create_invoice_after_payment(so, so.order_line) # Create invoice

                # Sending tickets to the attendees
                request.env['event.event'].send_tickets_to_attendees(attendees_sudo)
            else:
                print('Payment Canceled/Failed')
                request.env['event.registration'].search([('id', 'in', att_ids)]).update({'sale_status': 'to_pay'})
                # raise UserError(_("Payment Failed: We received your details. Please contact administrator for the payment related queries/details."))
                return request.render("website_event.payment_failed")
        
        else: # Show the already created invoice number
            return request.render("website_event.order_alread_created", {'order_id': order_id})
        
        return request.render("website_event.registration_complete", request.env['event.event']._get_registration_confirm_values(event, attendees_sudo, order_id))
        # return request.redirect(('/event/%s/registration/success?' % event_id) + werkzeug.urls.url_encode({'registration_ids': attids}))
      

    def _process_tickets_form(self, event, form_details):
        """ Process posted data about ticket order. Generic ticket are supported
        for event without tickets (generic registration).

        :return: list of order per ticket: [{
            'id': if of ticket if any (0 if no ticket),
            'ticket': browse record of ticket if any (None if no ticket),
            'name': ticket name (or generic 'Registration' name if no ticket),
            'quantity': number of registrations for that ticket,
        }, {...}]
        """
        ticket_order = {}
        for key, value in form_details.items():
            registration_items = key.split('nb_register-')
            if len(registration_items) != 2:
                continue
            ticket_order[int(registration_items[1])] = int(value)

        ticket_dict = dict((ticket.id, ticket) for ticket in request.env['event.event.ticket'].sudo().search([
            ('id', 'in', [tid for tid in ticket_order.keys() if tid]),
            ('event_id', '=', event.id)
        ]))

        return [{
            'id': tid if ticket_dict.get(tid) else 0,
            'ticket': ticket_dict.get(tid),
            'name': ticket_dict[tid]['name'] if ticket_dict.get(tid) else _('Registration'),
            'quantity': count,
        } for tid, count in ticket_order.items() if count]
    

    def _process_attendees_form(self, event, form_details):
        """ Process data posted from the attendee details form.
        Extracts question answers:
        - For both questions asked 'once_per_order' and questions asked to every attendee
        - For questions of type 'simple_choice', extracting the suggested answer id
        - For questions of type 'text_box', extracting the text answer of the attendee.

        :param form_details: posted data from frontend registration form, like
            {'1-name': 'r', '1-email': 'r@r.com', '1-phone': '', '1-event_ticket_id': '1'}
        """
        allowed_fields = request.env['event.registration']._get_website_registration_allowed_fields()
        registration_fields = {key: v for key, v in request.env['event.registration']._fields.items() if key in allowed_fields}
        for ticket_id in list(filter(lambda x: x is not None, [form_details[field] if 'event_ticket_id' in field else None for field in form_details.keys()])):
            if int(ticket_id) not in event.event_ticket_ids.ids and len(event.event_ticket_ids.ids) > 0:
                raise UserError(_("This ticket is not available for sale for this event"))
        registrations = {}
        general_answer_ids = []
        general_identification_answers = {}
        # as we may have several questions populating the same field (e.g: the phone)
        # we use this to hold the fields that have already been handled
        # goal is to use the answer to the first question of every 'type' (aka name / phone / email / company name)
        already_handled_fields_data = {}
        for key, value in form_details.items():
            if not value:
                continue

            key_values = key.split('-')
            # Special case for handling event_ticket_id data that holds only 2 values
            if len(key_values) == 2:
                registration_index, field_name = key_values
                if field_name not in registration_fields:
                    continue
                registrations.setdefault(registration_index, dict())[field_name] = int(value) or False
                continue

            registration_index, question_type, question_id = key_values
            answer_values = None
            if question_type == 'simple_choice':
                answer_values = {
                    'question_id': int(question_id),
                    'value_answer_id': int(value)
                }
            else:
                answer_values = {
                    'question_id': int(question_id),
                    'value_text_box': value
                }

            if answer_values and not int(registration_index):
                general_answer_ids.append((0, 0, answer_values))
            elif answer_values:
                registrations.setdefault(registration_index, dict())\
                    .setdefault('registration_answer_ids', list()).append((0, 0, answer_values))

            if question_type in ('name', 'email', 'phone', 'company_name')\
                and question_type not in already_handled_fields_data.get(registration_index, []):
                if question_type not in registration_fields:
                    continue

                field_name = question_type
                already_handled_fields_data.setdefault(registration_index, list()).append(field_name)

                if not int(registration_index):
                    general_identification_answers[field_name] = value
                else:
                    registrations.setdefault(registration_index, dict())[field_name] = value

        if general_answer_ids:
            for registration in registrations.values():
                registration.setdefault('registration_answer_ids', list()).extend(general_answer_ids)

        if general_identification_answers:
            for registration in registrations.values():
                registration.update(general_identification_answers)

        return list(registrations.values())