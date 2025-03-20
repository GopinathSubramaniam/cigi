import io

import xlsxwriter

from odoo import fields, models
from odoo.http import request


class ExportAttendeeWizard(models.TransientModel):
    _name = 'export.attendee.wizard'
    _description = 'Export Attendee Wizard'

    excel_file = fields.Binary('Download Excel File', readonly=True)
    file_name = fields.Char('Attendees', readonly=True)


    def export_attendees(self, event_id):
       
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Attendees')

        question_objs = self.env['event.question'].search([('event_id', '=', event_id)])
        question_titles = [q['title'] for q in question_objs]
        
        # Preparing the headers
        headers = ['Created On', 'Registered User', 'Registered Email', 'Registered Phone', 'Event', 'Sales Status']
        for q in question_titles:
            headers.append(('Attendee %s' % q))

        print('Headers = ', headers)
        row = 0
        col = 0

        # Write the headers
        for header in headers:
            worksheet.write(row, col, header)
            col += 1

        # Write attendee data
        row = 1
        attendees = self.env['event.registration'].search([('event_id', '=', event_id)])
        for attendee in attendees:
            worksheet.write(row, 0, str(attendee.create_date))
            worksheet.write(row, 1, attendee.name)
            worksheet.write(row, 2, attendee.email)
            worksheet.write(row, 3, attendee.phone)
            worksheet.write(row, 4, attendee.event_id.name)
            worksheet.write(row, 5, attendee.sale_status)
            print('attendee.sale_status = ', attendee.sale_status);

            # <> Adding the event registration answers
            idx = 6
            answers = self.env['event.registration.answer'].search([('registration_id', '=', attendee.id)])
            for a in answers:
                print('Answer Object = ', idx, 'Value = ', a);
                print('Answer = ', a.value_answer_id.name);

                val = a.value_text_box 
                if a.value_answer_id.name:
                    val = a.value_answer_id.name

                worksheet.write(row, idx, val or '')
                idx += 1
            # </>
            row += 1

        # Close the workbook
        workbook.close()

        # Get the Excel data
        output.seek(0)
        excel_file = output.read()

        # Encode the Excel file in base64
       
        print('Export Excel File')
        return excel_file