from odoo import models, fields, api

class CustomEvent(models.Model):
    _inherit = 'event.event'

    def download_attendees_excel(self):
        event_id = self.id
        print('Event Id = ', event_id)
        return {
            'type': 'ir.actions.act_url',
            'url': f'/download/event_attendees/{self.id}',
            'target': 'new',  # Opens the download in a new tab
        }
