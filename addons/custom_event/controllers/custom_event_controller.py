from odoo import http
from odoo.http import request
import io
import xlsxwriter

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