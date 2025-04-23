from odoo import models, fields, api
from datetime import timedelta, datetime
import calendar
from dateutil.relativedelta import relativedelta


class AccountMoveAllocateWizard(models.TransientModel):
    _name = 'account.move.allocate.wizard'
    _description = 'Allocate Journal Entries Wizard'
    _inherit = ['analytic.mixin']

    journal_id = fields.Many2one(
        'account.journal', string="Journal",
        domain=[('type', '=', 'general')], 
    )
    no_of_entries = fields.Integer(string="No. of Entries",default='1')
    starting_date = fields.Date(string="Starting Date",default=lambda self: self._default_starting_date())
    debit_account_id = fields.Many2one(
        'account.account', string="Debit Account"
       
    )
    credit_account_id = fields.Many2one(
        'account.account', string="Credit Account"
      
    )
    company_id = fields.Many2one(
        'res.company', string="Company"
    )
    total_amount = fields.Monetary(
        string="Total Amount", currency_field='currency_id'
    )
    allocated_amount = fields.Monetary(
        string="Allocated Amount", compute="_compute_allocated_amount", store=True
    )
    frequency = fields.Selection(
        [('monthly', 'Monthly')], string="Frequency",
        default='monthly', 
    )
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id, string="Currency")
    partner_id = fields.Many2one('res.partner')
    debit_account_readonly = fields.Boolean(string="Debit Account Readonly")
    credit_account_readonly = fields.Boolean(string="Credit Account Readonly")
    ending_date = fields.Date(string="Ending Date", compute="_compute_ending_date", store=True)

    
    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        active_id = self._context.get('active_id')

        if active_id:
            move_line = self.env['account.move.line'].browse(active_id)

            if move_line:
                balance = move_line.debit - move_line.credit
                if balance > 0:
                    defaults['credit_account_id'] = move_line.account_id.id
                    defaults['credit_account_readonly'] = True  
                elif balance < 0:
                    defaults['debit_account_id'] = move_line.account_id.id
                    defaults['debit_account_readonly'] = True  

        return defaults

    
    def _default_starting_date(self):
        active_id = self._context.get('active_id')
        if not active_id:
            return fields.Date.context_today(self)
    
        source_move = self.env['account.move.line'].browse(active_id).move_id
    
        if source_move and source_move.date:
            last_day = calendar.monthrange(source_move.date.year, source_move.date.month)[1]
            return source_move.date.replace(day=last_day)
    
        return fields.Date.context_today(self)


    @api.depends('total_amount', 'no_of_entries')
    def _compute_allocated_amount(self):
        for record in self:
            record.allocated_amount = record.total_amount / record.no_of_entries if record.no_of_entries else 0
            
    @api.depends('starting_date', 'no_of_entries', 'frequency')
    def _compute_ending_date(self):
        for record in self:
            if record.starting_date and record.no_of_entries > 0:
                current_date = record.starting_date
                for _ in range(record.no_of_entries - 1):
                    current_date += relativedelta(months=1)
                    last_day = calendar.monthrange(current_date.year, current_date.month)[1]
                    current_date = current_date.replace(day=last_day)
                record.ending_date = current_date
            else:
                record.ending_date = record.starting_date

    def action_create_entries(self):
        """Create multiple account.move records based on user input in the wizard."""
        self.ensure_one()
        move_obj = self.env['account.move']
        move_lines_obj = self.env['account.move.line']

        created_moves = []

        current_date = self.starting_date

        source_move = self.env['account.move.line'].browse(self._context.get('active_id')).move_id

        for i in range(self.no_of_entries):
            move_vals = {
                'date': current_date,
                'journal_id': self.journal_id.id,
                'company_id': self.company_id.id,
                  'ref': source_move.name,
                'currency_id': self.currency_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': self.debit_account_id.id,
                        'debit': self.allocated_amount,
                        'credit': 0.0,
                        'currency_id': self.currency_id.id,
                        'name': f"Allocation-{current_date.strftime('%d-%m-%y')}-{self.debit_account_id.name}",  
                        'partner_id': self.partner_id.id,
                        'analytic_distribution': self.analytic_distribution,
                    }),
                    (0, 0, {
                        'account_id': self.credit_account_id.id,
                        'debit': 0.0,
                        'credit': self.allocated_amount,
                        'currency_id': self.currency_id.id,
                         'name': f"Allocation-{current_date.strftime('%d-%m-%y')}-{self.credit_account_id.name}", 
                         'partner_id': self.partner_id.id,
                         'analytic_distribution': self.analytic_distribution,
                    }),
                ],
                'source_move_id': source_move.id,  
            }
            move = move_obj.create(move_vals)
            created_moves.append(move.id)
            #move.action_post()

            if self.frequency == 'monthly':
                next_month = current_date + relativedelta(months=1)
                last_day_next_month = calendar.monthrange(next_month.year, next_month.month)[1]
                current_date = next_month.replace(day=last_day_next_month)
        source_move.write({'allocated_move_ids': [(6, 0, created_moves)]})

        return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'account.move',
                    'res_id': source_move.id,
                    'view_mode': 'form',
                    'target': 'current',
                }
                
                
                
    