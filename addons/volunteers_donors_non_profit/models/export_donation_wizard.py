import io

import xlsxwriter

from odoo import fields, models
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class ExportDonationWizard(models.TransientModel):
    _name = 'export.donation.wizard'
    _description = 'Export Donation Wizard'

    excel_file = fields.Binary('Download Excel File', readonly=True)
    file_name = fields.Char('Attendees', readonly=True)


    def export_donations(self, campaign_id):
       
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Donations')

        # Preparing the headers
        headers = ['Created On', 'Customer', 'Email', 'Mobile', 'Payment Number', 'HDFC Ref', 'PAN', 'Amount']
        
        _logger.info(f'Headers = {headers}')
        
        # Write the headers in the 1st row
        for index, value in enumerate(headers):
            worksheet.write(0, index, value)

        donation_objs = self.env['volunteer.campaign.payment'].search([('volunteer_campaign_id', '=', campaign_id)])
        # Write attendee data
        row = 1
        for obj in donation_objs:
            worksheet.write(row, 0, str(obj.create_date))
            worksheet.write(row, 1, obj.partner_id.name)
            worksheet.write(row, 2, obj.user_email)
            worksheet.write(row, 3, obj.user_mobile)
            worksheet.write(row, 4, obj.invoice_num)
            worksheet.write(row, 5, obj.payment_ref_num)
            worksheet.write(row, 6, obj.pan_num)
            worksheet.write(row, 7, obj.amount)

            row += 1

        # Close the workbook
        workbook.close()

        # Get the Excel data
        output.seek(0)
        excel_file = output.read()

        # Encode the Excel file in base64
       
        print('Export Excel File')
        return excel_file