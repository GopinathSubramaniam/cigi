from odoo import models, fields, api

class CustomEvent(models.Model):
    _inherit = 'event.event'

    tag_ids = fields.Many2many('event.tag', string="Tags", readonly=False, required=True)

    def download_attendees_excel(self):
        event_id = self.id
        print('Event Id = ', event_id)
        return {
            'type': 'ir.actions.act_url',
            'url': f'/download/event_attendees/{self.id}',
            'target': 'new',  # Opens the download in a new tab
        }
    
    def apply_coupon_to_event_registration(self, event_registration_id, coupon_code):
        # Apply a coupon to a specific event registration by its ID
        
        # Get the event registration
        event_registration = self.env['event.registration'].browse(event_registration_id)

        # Check if the event registration exists
        if not event_registration:
            raise ValueError(f"Event registration with ID {event_registration_id} not found.")

        # Get the coupon program based on the coupon code
        coupon = self.env['sale.coupon'].search([('code', '=', coupon_code)], limit=1)

        # Check if the coupon exists
        if not coupon:
            raise ValueError(f"Coupon with code {coupon_code} not found.")

        # Apply the coupon to the event registration
        try:
            event_registration.apply_coupon(coupon_code)
            event_registration._compute_amount()  # Recalculate the registration totals after applying the coupon
            print(f"Coupon {coupon_code} applied successfully to Event Registration {event_registration_id}.")
        except Exception as e:
            raise ValueError(f"Failed to apply coupon: {str(e)}")

    def validate_coupon(self, promo_code, amount_total):
        loyalty_rule = self.env['loyalty.rule'].sudo().search([('code', '=', promo_code),('active', '=', True)], limit=1)
        
        if not loyalty_rule:
            return { 'success': False, 'message': f"The coupon '{promo_code}' is not available.", 'is_valid': False }
        else:
            # Step 2: Check if the coupon is active and not expired
            if loyalty_rule.minimum_amount and amount_total < loyalty_rule.minimum_amount:
                return { 'success': False, 'message': f"Order must be at least {loyalty_rule.minimum_amount} to use this promo code.", 'is_valid': False }
            else: 
                loyalty_reward = self.env['loyalty.reward'].sudo().search([('program_id', '=', loyalty_rule.program_id.id)], limit=1)
                discount_amount = 0.00
                if loyalty_reward.discount_mode == 'percent':
                    discount_amount = (amount_total * loyalty_reward.discount / 100)
                    discounted_amount = amount_total - discount_amount
                
                return { 'success': True, 'message': f"The coupon '{promo_code}' is valid.", 'is_valid': True, 'discounted_amount': discounted_amount }

    def get_discount_amount(self, promo_code, amount_total):
        loyalty_rule = self.env['loyalty.rule'].sudo().search([('code', '=', promo_code),('active', '=', True)], limit=1)
        discount_amount = 0.00
        if amount_total >= loyalty_rule.minimum_amount:
            loyalty_reward = self.env['loyalty.reward'].sudo().search([('program_id', '=', loyalty_rule.program_id.id)], limit=1)
            if loyalty_reward.discount_mode == 'percent':
                discount_amount = (amount_total * loyalty_reward.discount / 100)

        return discount_amount
    
    def get_loyal_reward_product_id(self, promo_code):
        loyalty_rule = self.env['loyalty.rule'].sudo().search([('code', '=', promo_code),('active', '=', True)], limit=1)
        loyalty_reward = self.env['loyalty.reward'].sudo().search([('program_id', '=', loyalty_rule.program_id.id)], limit=1)
        return loyalty_reward
    
    def _create_attendees_from_registration_post(self, event, registration_data):
        """ Also try to set a visitor (from request) and
        a partner (if visitor linked to a user for example). Purpose is to gather
        as much informations as possible, notably to ease future communications.
        Also try to update visitor informations based on registration info. """
        visitor_sudo = self.env['website.visitor']._get_visitor_from_request(force_create=True)

        registrations_to_create = []
        for registration_values in registration_data:
            registration_values['event_id'] = event.id
            if not registration_values.get('partner_id') and visitor_sudo.partner_id:
                registration_values['partner_id'] = visitor_sudo.partner_id.id
            elif not registration_values.get('partner_id'):
                registration_values['partner_id'] = False if self.env.user._is_public() else self.env.user.partner_id.id

            # update registration based on visitor
            registration_values['visitor_id'] = visitor_sudo.id

            registrations_to_create.append(registration_values)
            
        attendees_sudo = self.env['event.registration'].sudo().create(registrations_to_create)
        
        # Adding event tags in contacts 
        attach_tag_ids = []
        for tag in attendees_sudo[0].event_id.tag_ids:
            t = self.env['res.partner.category'].search([('name', '=', tag.name)], limit=1)
            if not t:
                created_tag = self.env['res.partner.category'].create({ 'name': tag.name})
                attach_tag_ids.append(created_tag.id)
            else:
                attach_tag_ids.append(t.id)
        
        # Creating contacts if not available
        contact_id = None
        for atte in attendees_sudo:
            existing_cont = self.env["res.partner"].sudo().search([('email', '=', atte['email'])], limit=1)
            if not existing_cont:
                contact = {
                    "name": atte['name'],
                    "complete_name": atte['name'],
                    "email": atte['email'],
                    "mobile": atte['phone'],
                    "city": '',
                    "active": True,
                    'company_id': 1 # Default company id
                }
                # Adding the event tags with contacts
                if(len(attach_tag_ids) > 0):
                    contact['category_id'] =  [(6, 0, attach_tag_ids)]
                
                contact = self.env["res.partner"].sudo().create(contact)  # Create contact data in res.partner model
                if contact_id is None:
                    contact_id = contact.id
            else:
                if contact_id is None:
                    contact_id = existing_cont.id
        # </>

        return {'attendees_sudo': attendees_sudo, 'contact_id': contact_id}
    
    def _get_registration_confirm_values(self, event, attendees_sudo, order_id):
        urls = event._get_event_resource_urls()
        return {
            'attendees': attendees_sudo,
            'event': event,
            'google_url': urls.get('google_url'),
            'iCal_url': urls.get('iCal_url'),
            'order_id': order_id,
            'price': attendees_sudo[0].event_ticket_id.price
        }

    def send_event_tickets_mail(registrations):
        for registration in registrations:
            if registration.sale_order_id:
                registration.message_post_with_source(
                    'mail.message_origin_link',
                    render_values={'self': registration, 'origin': registration.sale_order_id},
                    subtype_xmlid='mail.mt_note',
                )

    def send_tickets_to_attendees(self, attendees):
        # Get the event object
        if attendees and len(attendees) > 0:
            template = self.env.ref('event.event_subscription', raise_if_not_found=False)
            for registration in attendees:
                if registration.sale_order_id:
                    template.sudo().send_mail(registration.id, force_send=True)

            return f"Sent tickets to {len(attendees)} attendees"
    


           


           