# -*- coding: utf-8 -*-

import base64
import xlrd
import datetime

from odoo import models,fields,api,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class ImportProjectTaskWizard(models.TransientModel):
    _name = "multiple.task.import"
    _description = 'Import Project Task Wizard'

    files = fields.Binary(
        string = "Import Excel File",
    )
    company_id = fields.Many2one(
        'res.company',
        string = "Company",
        required = True,
    )
    import_by = fields.Selection(
        [('task','Task'),
        ('project_task','Project')],
        string = "Import",
        default = 'task',
        required = True,
    )
  
#    @api.multi #odoo13
    def import_project_task(self):
        project_obj = self.env['project.project']
        user_obj = self.env['res.users']
        tag_obj = self.env['project.tags']
        customer_obj = self.env['res.partner']
        task_obj = self.env['project.task']
        
        if self.import_by == 'task':
            
            try:
                workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
                # workbook = xlrd.open_workbook(file_contents = base64.encodebytes(self.files))

            except:
                raise ValidationError("Please select .xls/xlsx file.")
            
            sheet_name = workbook.sheet_names()
            sheet = workbook.sheet_by_name(sheet_name[0])
            number_of_rows = sheet.nrows
            
            task_list =[]
            tags_list = []
            row = 1
            
            while(row < number_of_rows):
                title = sheet.cell(row,0).value
                if not title:
                    raise ValidationError('Task name should not be empty at row %s in excel file.'%(row+1))

                project_id = sheet.cell(row,1).value
                if project_id:
                    projectId = project_obj.search([('name', '=', project_id)], limit=1)

                user_id=sheet.cell(row,2).value
                if user_id:
                    assigned_to = user_obj.search([('name', '=', user_id)], limit=1)
                if not assigned_to:
                    raise ValidationError('%s User is invalid at row number %s '%(sheet.cell(row,2).value,row+1))
                
                datestart = sheet.cell(row,3).value
                deadline = sheet.cell(row,4).value

                tag_ids = sheet.cell(row,5).value
                tags_list = tag_ids.split(',')
                tags_id = tag_obj.search([('name', 'in', tags_list)])

                sequence = sheet.cell(row,6).value
                parent_id = sheet.cell(row,7).value
                if parent_id:
                    parent = task_obj.search([('name', '=', parent_id)], limit=1)
                
                description = sheet.cell(row,8).value
                
                partner_id = sheet.cell(row,9).value
                if partner_id:
                    partner = customer_obj.search([('name', '=', partner_id)], limit=1)
                    
                email_from = sheet.cell(row,10).value
                watcher_email = sheet.cell(row,11).value

                date_start = datetime.strptime(datestart, '%m-%d-%Y') #odoo13
                date_deadline = datetime.strptime(deadline, '%m-%d-%Y') #odoo13
                vals = { 
                    'name' : title,
                    'project_id' : projectId.id,
                    # 'activity_user_id' : assigned_to.id,
                    'user_ids': [(4, assigned_to.id)],
                    'date_deadline' : date_deadline.strftime(DEFAULT_SERVER_DATE_FORMAT), #odoo13
                    'tag_ids' : [(6,0,tags_id.ids)],
                    'sequence' : sequence,
                    'parent_id' : parent.id,
                    'company_id' : self.company_id.id,
                    'partner_id' : partner.id,
                    'description' : description,
                    # 'email_from' : email_from,
                    'email_cc' : email_from,

                    'email_cc' : watcher_email,
                    'date_assign' : date_start.strftime(DEFAULT_SERVER_DATE_FORMAT), #odoo13
                }
                row = row + 1
                task_id = self.env['project.task'].create(vals)
                
                task_list.append(task_id.id)
                if task_id:
                    action = self.env.ref('project.action_view_task').sudo().read()[0]
                    action['domain'] = [('id','in',task_list)]
            return action

        elif self.import_by == 'project_task':

            try:
                workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
            except:
                raise ValidationError("Please select .xls/xlsx file.")
            sheet_name = workbook.sheet_names()
            sheet = workbook.sheet_by_name(sheet_name[0])
            number_of_rows = sheet.nrows
            list_project = []
            manager = self.env['res.users']
            
            row = 1
            while(row < number_of_rows):
                project_name = sheet.cell(row,0).value
                if not project_name:
                    raise ValidationError('Project name should not be empty at row %s in excel file .'%(row+1))

                user_id = sheet.cell(row,1).value
                if user_id:
                    project_manager = manager.search([('name', '=', user_id)], limit=1)

                privacy = sheet.cell(row,2).value
                partner_id = sheet.cell(row,3).value
                if partner_id:
                    customer_id = customer_obj.search([('name', '=', partner_id)], limit=1)

                sequence = sheet.cell(row,4).value
                project_vals = { 
                    'name' : project_name,
                    'user_id' : project_manager.id,
                    'privacy_visibility' : privacy,
                    'partner_id' : customer_id.id,
                    'sequence' : sequence,
                    'company_id' : self.company_id.id,
                }

                row = row + 1
                project_id =self.env['project.project'].create(project_vals)
                list_project.append(project_id.id)
                
                if project_id:
                    action = self.env.ref('project.open_view_project_all').sudo().read()[0]
                    action['domain'] = [('id','in',list_project)]
            return action
